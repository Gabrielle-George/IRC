import socket
from time import sleep
import selectors
import sys
from threading import Thread
from IRCparse import IRCcommands, parse

HOST, PORT = sys.argv[1], int(sys.argv[2])

G_quit = False
cmds = IRCcommands()
curRoom = ""

def readInput(s):
    global G_quit
    global cmds
    global curRoom
    while not G_quit:
        usrMsg = input()
        if usrMsg[0]!="/":
            #they are just typing into whatever chat window they had last
            #TODO: have the client keep track of this
            if curRoom != "": #curRoom is None?
                s.sendall(bytes("{} {} {}\r\n".format('ROOMMSG', curRoom, usrMsg),"utf-8"))
            # else:
            #     s.sendall(bytes("{} {}\r\n".format('DEFAULT', usrMsg),"utf-8"))
        else:
            print('usgmsg in else', usrMsg)
            #we have a command, parse it!
            cmd, payload = parse(usrMsg)
            print('cmd is:', cmd, 'payload is', payload)
            if cmd == cmds.joinUSR:
                s.sendall(bytes("{} {}\r\n".format(cmds.JOINROOM,payload),"utf-8"))
                curRoom = payload.split()[0]
            if cmd == cmds.quitUSR:
                #TODO: send disconnect request to server.
                G_quit =True
            if cmd in IRCcommands.messagetypes:
                print('cmd is in here', cmd)
                args = payload
                msg = "{} {} \r\n".format(cmd, args)
                print("msg is ", msg)
                s.sendall(bytes(msg.strip(),"utf-8"))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    t = Thread(group=None,target=readInput, name="ReadsFromStdin",args=[s])
    t.start()

    while not G_quit:
        data = s.recv(1024)
        to_print = data.decode("utf-8")
        print(to_print)