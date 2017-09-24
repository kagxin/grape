import asyncio
import sys
import pipes
import os
import traceback
import json
import logging
from django.conf import settings


LOGGINGFILE = {}

if 'handlers' in  settings.LOGGING.keys():
    for handler_name, _ in settings.LOGGING['handlers'].items():
        for name, filename in settings.LOGGING['handlers'][handler_name].items():
            if name == 'filename':
                LOGGINGFILE.setdefault(handler_name, filename)
print(LOGGINGFILE)

class FileException(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return 'GrapeException:{}'.format(self.message)


class ProxyControl:

    def __init__(self, *args, **kwargs):
        self.writers = {}
        self.log = None

    def __str__(self):
        return 'ProxyControl:<{}>'.format(self.writers)

    def set_log(self, writer, log):
        self.writers.update(writer, log)

    def register(self, writer, log):
        self.writers.setdefault(writer, self.log)

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
                for writer, log in proxy.writers.items():
                    try:
                        if log == read_file:
                            writer.write(line.encode('utf-8'))
                            await writer.drain()
                    except:
                        proxy.unregister(writer)
                        logging.error('writer error!68')
                else:
                    await asyncio.sleep(s)

async def tcp_handle(reader, writer, **kwargs):

    proxy.register(writer, None)
    try:
        writer.write(json.dumps(LOGGINGFILE).encode('utf-8'))
        await writer.drain()
    except:
        proxy.unregister(writer)
        logging.error('writer error!80')
    
    while True:
        data = await reader.readline()
        try:
            print(data.decode())
            sys.stdout.flush()
            msg = json.loads(data.decode())
        except:
            proxy.unregister(writer)
            logging.error('data error close writer!89')
            writer.close()
            break
            
        else:
            if msg['log'] in LOGGINGFILE.keys():
                proxy.set_log(writer, msg['log'])
            
        """    
        try:
            writer.write(data)
            await writer.drain()
        except:
            proxy.unregister(writer)
            logging.error('writer error!')
        """

def grape_main():
        
    loop = asyncio.get_event_loop()
    
    tcp_server = asyncio.start_server(tcp_handle, '0.0.0.0', 8080, loop=loop)
    
    tasks = [
        asyncio.ensure_future(tcp_server)
    ]
    tasks.extend([asyncio.ensure_future(tail(filename, proxy, s=0.5)) for _, filename in LOGGINGFILE.items()])
    
    loop.run_until_complete(asyncio.wait(tasks))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    

if __name__ ==  '__main__':
    grape_main()
    
