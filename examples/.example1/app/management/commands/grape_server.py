import asyncio
import sys
import os
import json
import logging
from json.decoder import JSONDecodeError
from django.conf import settings
from django.contrib.auth import authenticate

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s', filename='/tmp/gserver.log', filemode='a+')

def log_asyncio_exception_decorator(coro):
    async def handle_exception(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except Exception as e:
            logging.exception(str(e))
            raise
    return handle_exception


class GrapeException(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return 'GrapeException:{}'.format(self.message)


class FileDoesNotExistException(GrapeException):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return 'GrapeException:{}'.format(self.message)


def wrap_send_data(data):

    return (json.dumps(data) + '\n').encode('utf-8')


def get_get_data(data):
    return json.loads(data.decode('utf-8'))


class GrapeServer:

    def __init__(self):
        self.files = self.get_log_file()
        self.topic_to_sub = {}
        print(self.files)

    def get_log_file(self):
        log_files = {}
        if 'handlers' in settings.LOGGING.keys():
            for handler_name, _ in settings.LOGGING['handlers'].items():
                for name, filename in settings.LOGGING['handlers'][handler_name].items():
                    if name == 'filename':
                        log_files.setdefault(handler_name, filename)
        return log_files

    def add_sub(self, topic, sub_writer):
        if topic not in self.topic_to_sub:
            self.topic_to_sub.setdefault(topic, []).append(sub_writer)
        else:
            self.topic_to_sub[topic].append(sub_writer)
        return

    def update_sub(self, topic, sub_writer):
        self.rm_sub(sub_writer)
        self.add_sub(topic, sub_writer)
        return

    def rm_sub(self, sub_writer):
        for topic, subs in self.topic_to_sub.items():
            if sub_writer in subs:
                self.topic_to_sub[topic].remove(sub_writer)
                logging.info('rm writer{}'.format(sub_writer))
                return True
        return False
    @log_asyncio_exception_decorator
    async def tail(self, file_path, s=0.5):

        if not os.access(file_path, os.F_OK):
            raise FileDoesNotExistException(
                'File {} does not exist!'.format(file_path))

        with open(file_path) as _file:
            _file.seek(0, 2)
            while True:
                curr_p = _file.tell()
                line = _file.readline()
                if not line:
                    _file.seek(curr_p)
                    await asyncio.sleep(s)
                else:
                    for topic, subs in self.topic_to_sub.items():
                        if self.files[topic] == file_path:
                            for writer in subs:
                                try:
                                    writer.write(line.encode('utf-8'))
                                    await writer.drain()
                                except ConnectionResetError:
                                    self.rm_sub(writer)
                                    writer.close()
                            else:
                                await asyncio.sleep(s)
                    else:
                        await asyncio.sleep(s)


    @log_asyncio_exception_decorator
    async def tcp_handle(self, reader, writer):
        print(reader, writer)
        try:
            data = await reader.readline()
            print(json.loads(data.decode('utf-8')))
            if authenticate(**json.loads(data.decode('utf-8'))):
                auth_status = {'status': 1}
            else:
                auth_status = {'status': 0}
            writer.write(wrap_send_data(auth_status))
            await writer.drain()

            writer.write(wrap_send_data(self.files))
            await writer.drain()
        except ConnectionResetError:
            self.rm_sub(writer)
            writer.close()

        while True:
            try:
                data = await reader.readline()
                print(data.decode())
                sys.stdout.flush()
                msg = json.loads(data.decode())
            except ConnectionResetError:
                logging.info('The client is disconnected!')
                self.rm_sub(writer)
                writer.close()
                break
            except JSONDecodeError:
                logging.info('The client data format error!')
                self.rm_sub(writer)
                writer.close()
                break
            except Exception as e:
                logging.exception(str(e))
                self.rm_sub(writer)
                writer.close()
                break
            else:
                if msg['topic'] in self.files.keys():
                    self.update_sub(msg['topic'], writer)
                elif not msg['topic']:
                    self.rm_sub(writer)

                logging.info(self.topic_to_sub)

        return 123

    def start_server(self, loop):

        loop.set_debug(True)

        tasks = []
        tcp_server_task = asyncio.start_server(
            self.tcp_handle, '0.0.0.0', 8080, loop=loop)

        tasks.append(
            asyncio.ensure_future(tcp_server_task)
        )
        tasks.extend([asyncio.ensure_future(self.tail(path, 0.2))
                      for _, path in self.files.items()])
        print(tasks)
        for res in loop.run_until_complete(asyncio.wait(tasks)):
            print(res)

        return tasks


def grape_main():
    loop = asyncio.get_event_loop()
    grape_server = GrapeServer()
    tasks = grape_server.start_server(loop)

    loop.run_forever()


if __name__ == '__main__':
    grape_main()
