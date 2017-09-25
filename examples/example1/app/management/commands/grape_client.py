import asyncio
import cmd
import json
import socket
import threading
import sys
from turtle import *

HOST = 'localhost'
PORT = 8080

sock = socket.socket()
try:
    sock.connect((HOST, PORT))
except:
    raise
    print('connect error!')

try:
    handles = json.loads(sock.recv(1024).decode())
    print(handles)
except:
    print('get json error!')


class TurtleShell(cmd.Cmd):
    intro = 'Welcome to the turtle shell.   Type help or ? to list commands.\n'
    prompt = '(turtle) '

    def do_undo(self, arg):
        'Undo (repeatedly) the last turtle action(s):  UNDO'
    def do_reset(self, arg):
        'Clear the screen and return turtle to center:  RESET'
        reset()
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
    

if __name__ == '__main__':
    t1 = threading.Thread(target=handle)
    t2 = threading.Thread(target=TurtleShell().cmdloop)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
