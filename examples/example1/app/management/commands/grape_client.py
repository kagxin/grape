import asyncio
import signal
import cmd
import os
import json
import sys
import logging
import pdb
from queue import Queue, Empty
from json.decoder import JSONDecodeError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CWD_DIR = os.getcwd()

HOST = 'localhost'
PORT = 8080
CONF = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', filename='/tmp/gclient.log', filemode='a+')

def exit_handler():
    for task in asyncio.Task.all_tasks():
        task.cancel()

def wrap_send_data(data):

    return (json.dumps(data)+'\n').encode('utf-8')

def get_get_data(data):
    return json.loads(data.decode('utf-8'))

async def auth(writer, reader):
    if len(sys.argv) != 5:
        print('\nUsage : python -m grape_client server port user password.\nexample: python -m grape_clent 192.168.0.1 8000 username password')
        sys.stdout.flush()
        os._exit(-1)
    writer.write(wrap_send_data({'username':sys.argv[-2], 'password':sys.argv[-1]}))
    await writer.drain()
    data = await reader.readline()
    cmd = get_get_data(data)
    if cmd['status'] == 0:
        print('Authorization Failed!')
        sys.stdout.flush()
        os._exit(-1)
    else:
        pass


class GrapeClientShell(cmd.Cmd):
    intro = 'Welcome to the grape.  A remote logging tool for django.\n'
    prompt = '(grape)'

    def __init__(self, loop, queue):
        super(GrapeClientShell, self).__init__()
        self.loop = loop
        self.queue = queue

    def send_data(self, arg, data):
        self.queue.put(data)

    def do_trace(self, arg):
        'trace the logging of django handler: TRACE'
        if arg in CONF.keys():
            data = {'topic':arg}
        elif arg == 'off':
            data = {'topic':None}
        else:
            print('*** Unknown arg: %s\n' % arg)
            return 

        self.send_data(arg ,data)

    def complete_trace(self, text, line, begidx, endidx):
        com = list(CONF.keys())
        com.append('off')
        return com

    def do_bye(self, arg):
        'Stop logging, close the window, and exit:  BYE'
        os._exit(-1)
        return True


class GrapeClient:

    def __init__(self, host, port, queue, loop):
        self.queue = queue
        self.host = host
        self.port = port
        self.loop = loop
        self.logfile = open(CWD_DIR+'/gclient.log', 'a')
        self.writer = None
        self.reader = None

    async def read_con(self):
        while not self.reader:
            await asyncio.sleep(0.5)

        while True:
            data = await self.reader.readline()
            data_str = data.decode('utf-8')
            global CONF
            if not CONF:
                try:
                    CONF = json.loads(data_str.rstrip('\n'))
                except JSONDecodeError:
                    print('Server data error : {}'.format(data_str))
                    logging.exception(data_str.rstrip('\n'))
                    sys.stdout.flush()
                    os._exit(-1)
            else:
                sys.stdout.write(data_str)
                self.logfile.flush() 

    async def write_con(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
            await auth(self.writer, self.reader)
        except ConnectionRefusedError:
            print('The service is not started! Client exit.')
            os._exit(-1)
        while True:
            try:
                send_data = self.queue.get_nowait()
            except Empty:
                await asyncio.sleep(1)
            else:
                try:
                    self.writer.write(wrap_send_data(send_data))
                    await self.writer.drain()
                    logging.info('send_data to grapeserver {}'.format(send_data))
                except Exception as e:
                    logging.exception(str(e))

    def start(self):

        tasks = [
            asyncio.ensure_future(self.read_con()),
            asyncio.ensure_future(self.write_con())
            ]
        return tasks

    def stop(self):
        if self.writer:
            self.writer.close()
        self.logfile.close()

if __name__ == '__main__':


    q = Queue()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, exit_handler)

    client = GrapeClient(HOST, PORT, q, loop)
    tasks = client.start()
    f = loop.run_in_executor(None, GrapeClientShell(loop, q).cmdloop)

    tasks.append(asyncio.ensure_future(f))

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        print(str(e))
        raise
    finally:
        client.stop()
        loop.close()
