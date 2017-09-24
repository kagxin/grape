import asyncio
import sys
import pipes
import os
import traceback
import logging

class FileException(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return 'GrapeException:{}'.format(self.message)


class ProxyControl:

    def __init__(self, *args, **kwargs):
        self.writers = {}
        self.level = 'debug'

    def __str__(self):
        return 'ProxyControl:<{}>'.format(self.writers)

    def set_level(self, writer, level):
        self.writers[writer] = level

    def register(self, writer, level):
        self.writers.setdefault(writer, self.level)

    def unregister(self, writer):
        self.writers.pop(writer, None)

proxy = ProxyControl()

async def tail(read_file, proxy, s=1):

    if not os.access(read_file, os.F_OK):
        raise FileException('File {} does not exist!'.format(read_file))
    
    with open(read_file) as _file:
        _file.seek(0, 2)
        while True:
            curr_p = _file.tell()
            line = _file.readline()
            if not line:
                
                _file.seek(curr_p)
                await asyncio.sleep(s)
            else:
                for writer, level in proxy.writers.items():
                    try:
                        writer.write(line.encode('utf-8'))
                        await writer.drain()
                    except:
                        proxy.unregister(writer)                        
                        logging.error('writer error!')
                else:
                    await asyncio.sleep(s)

async def tcp_handle(reader, writer, **kwargs):

    proxy.register(writer, 'debug')

    while True:
        data = await reader.readline()
        try:
            writer.write(data)
            await writer.drain()
        except:
            proxy.unregister(writer)
            logging.error('writer error!')


def grape_main():
    loop = asyncio.get_event_loop()
    
    tcp_server = asyncio.start_server(tcp_handle, '0.0.0.0', 8080, loop=loop)
    tasks = [
        asyncio.ensure_future(tail('/Users/kangxin/Program/py3env/program/grape/examples/example1/debug.log', proxy, s=0.5)),
        asyncio.ensure_future(tcp_server)
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    
    print('grape_main end!')


if __name__ ==  '__main__':
    grape_main()
    
