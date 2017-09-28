import asyncio
import signal
import cmd
import os
import json
from json.decoder import JSONDecodeError
import sys
import logging
import pdb
from queue import Queue, Empty
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CWD_DIR = os.getcwd()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', filename='/tmp/aclient_log.txt', filemode='a+')


HOST = 'localhost'
PORT = 8080
STOP = False
CONF = {}

def my_handler():
    for task in asyncio.Task.all_tasks():
        task.cancel()


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
        self.loop()
        STOP = True
        return True


class GrapeClient:

    def __init__(self, host, port, queue, loop):
        self.queue = queue
        self.host = host
        self.port = port
        self.loop = loop
        self.logfile = open(CWD_DIR+'/aclient.log', 'a')
        self.writer = None
        self.reader = None

    async def read_con(self):
        flag = 0
        while not self.reader:
            await asyncio.sleep(0.5)
            
        while True:
            data = await self.reader.readline()
            data_str = data.decode('utf-8')
            sys.stdout.write(data_str)
            self.logfile.write(data_str)
            self.logfile.flush()
            if not flag:
                global CONF
                flag = 1
                try:
                    CONF = json.loads(data_str.rstrip('\n'))
                except JSONDecodeError:
                    logging.exception(data_str.rstrip('\n'))
        

    async def write_con(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
        while True:
            try:
                send_data = self.queue.get_nowait()
            except Empty:
                await asyncio.sleep(1)
            else:
                self.writer.write((send_data+'\n').encode('utf-8'))
                await self.writer.drain()

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
    loop.add_signal_handler(signal.SIGINT, my_handler)

    client = GrapeClient(HOST, PORT, q, loop)
    tasks = client.start()
    f = loop.run_in_executor(None, GrapeClientShell(loop, q).cmdloop)

    tasks.append(asyncio.ensure_future(f))

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        print(str(e))
    finally:
        client.stop()
        loop.close()