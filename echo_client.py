import socket
from time import sleep
import selectors
import sys
from threading import Thread
from IRCparse import IRCcommands

HOST, PORT = sys.argv[1], int(sys.argv[2])

G_quit = False
cmds = IRCcommands()

def readInput(s):
    global G_quit
    global cmds
    while not G_quit:
        usrMsg = input()
        if usrMsg[0]!="\\":
            #they are just typing into whatever chat window they had last
            #TODO: have the client keep track of this
            s.sendall(bytes("{} {}\r\n".format(cmds.LEAVE, usrMsg),"utf-8"))
        else:
            #we have a command, parse it!
            cmd = usrMsg.split()[0]
            if cmd == cmds.joinUSR:
                s.sendall(bytes("JOIN {}\r\n".format(usrMsg),"utf-8"))
            if cmd == cmds.quitUSR:
                #send disconnect request to server.
                G_quit =True
                



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    t = Thread(group=None,target=readInput, name="ReadsFromStdin",args=[s])
    t.start()

    while not G_quit:
        data = s.recv(1024)
        print(f"Received {data!r}")