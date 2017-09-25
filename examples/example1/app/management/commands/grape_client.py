import asyncio
import cmd
import json
from json.decoder import JSONDecodeError
import socket
import threading
import sys
import logging

EXIT = False

HOST = 'localhost'
PORT = 8080

sock = socket.socket()
try:
    sock.connect((HOST, PORT))
except ConnectionRefusedError:
    print('连接被拒绝可能是，未开启服务端！')
    sys.exit(-1)

try:
    handles = json.loads(sock.recv(1024).decode())
    print("""Usage:\n    trace {}
    """.format('/'.join(handles.keys())+'/off'))
except JSONDecodeError:
    print('服务端数据错误!')    
    sys.exit(-1)


class GrapeClientShell(cmd.Cmd):
    intro = 'Welcome to the turtle shell.   Type help or ? to list commands.\n'
    prompt = '(grape)'
    def send_data(self, dct):
        global sock
        log = dct.get('log')
        if log not in handles.keys():
            print('{}无效的参数，可选参数为：{}'.format(log, ','.join(handles.keys())))
        try:
           data =  json.dumps(dct) + '\n'
           sock.sendall(data.encode('utf-8'))
        except (JSONDecodeError, ConnectionResetError):
            print('断开连接！')
            sys.exit(-1)
    def do_trace(self, arg):
        data = json.dumps({'log':arg})+'\n'
        print(data)
        sock.sendall(data.encode('utf-8'))
    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Thank you for using Turtle')
        self.close()
        bye()
        return True
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

def handle():
    global sock
    while True:
        data = sock.recv(1024)
        print(data)
        if not data:
            sys.exit(-1)

if __name__ == '__main__':
    t1 = threading.Thread(target=handle)
    t2 = threading.Thread(target=GrapeClientShell().cmdloop)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
