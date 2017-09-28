import asyncio
import cmd
import json
from json.decoder import JSONDecodeError
import sys
import logging
import pdb
from queue import Queue, Empty

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

HOST = 'localhost'
PORT = 8080
CONF = {}

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
        data = json.dumps({'log':arg})
        self.send_data(arg ,data)

    def do_bye(self, arg):
        'Stop recording, close the window, and exit:  BYE'
        self.loop.stop()
        return True


class GrapeClient:

    def __init__(self, host, port, queue, loop):
        self.queue = queue
        self.host = host
        self.port = port
        self.loop = loop
        self.writer = None
        self.reader = None

    async def read_con(self):
        logging.info('enter read_con!')
        flag = 0
        while not self.reader:
            await asyncio.sleep(0.5)
        self.queue.put(json.dumps({'log':'file'}))
            
        while True:
            logging.info('waitting reader.')
            data = await self.reader.readline()
            data_str = data.decode('utf-8')
            logging.info('reader:'+data_str)
            if not flag:
                flag = 1
                global CONF
                try:
                    CONF = json.loads(data_str.rstrip('\n'))
                except:
                    logging.exception(data_str.rstrip('\n'))
        

    async def write_con(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
        while True:
            try:
                send_data = self.queue.get_nowait()
            except Empty:
                logging.error('asfsadfasdfasdf')
                await asyncio.sleep(1)
            else:
                self.writer.write((send_data+'\n').encode('utf-8'))
                await self.writer.drain()
                logging.info('writer:'+send_data)
                

    def start(self):

        tasks = [
            asyncio.ensure_future(self.read_con()),
            asyncio.ensure_future(self.write_con())
            ]
        
        return tasks
    
    def stop(self):
        if self.reader:
            self.reader.close()
        if self.writer:
            self.writer.close()

if __name__ == '__main__':

    q = Queue()
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    client = GrapeClient(HOST, PORT, q, loop)
    tasks = client.start()
    # f = loop.run_in_executor(None, GrapeClientShell(loop, q).cmdloop)
    # tasks.append(asyncio.ensure_future(f))
    # for t in tasks:
    #     logging.info(str(t))

    loop.run_until_complete(asyncio.wait(tasks))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.error('KeyboardInterrupt exit!')
        client.stop()
        loop.stop()
        raise
