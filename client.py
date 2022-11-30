import socket
from time import sleep
import selectors
import sys
from threading import Thread
from IRCparse import *

HOST, PORT = sys.argv[1], int(sys.argv[2])

class Client():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curRoom = None
        self.G_quit = False
        self.rooms = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def run(self):
        self.s.connect((HOST, PORT))
        t = Thread(group=None,target=client.readInput, name="ReadsFromStdin",args=[self.s])
        t.start()
        while not self.G_quit:
            data = self.s.recv(1024)
            serverMsg = self.parseServerMessage(data.decode('utf-8'))
            self.executeServerMessage(serverMsg)            
    
    def parseUserCommand(self, entry:str) -> Message:
        cmd = entry.split(' ')[0]
        match cmd:
            #user typed "/connect HOST PORT"
            case "/connect":
                host = entry.split(' ')[1]
                port = entry.split(' ')[2]
                return Connect(host, port)
            #user typed "/listrooms"
            case "/listrooms":
                return ListRooms()
            #user typed "/join roomname"
            case "/join":
                roomname = entry.split(' ')[1]
                print(f"found a join message, body: {roomname}")
                print(f"message as string: {JoinRoom(roomname=roomname)}")
                return JoinRoom(roomname=roomname)
            #user typed "/leave roomname"
            case "/leave":
                roomname = entry.split(' ')[1]
                return LeaveRoom(roomname)
            #user typed "/list roomname"
            case "/list":
                roomname = entry.split(' ')[1]
                return ListRoomUsers(roomname)
            #usertyped "/msg messagebody"
            case "/msg":
                message = ' '.join(entry.split(' ')[1:])
                print("sending to room: " + message)
                return MessageRoom(self.curRoom, message)
            #user typed "/msgroom #roomname : messageBody"
            case "/msgroom":
                roomname = entry.split(' ')[1][1:] #get roomname without '#'
                message = entry.split(':')[1].strip()
                return MessageRoom(roomname, message)
            case "/quit":
                return Quit()
        
    def parseServerMessage(self, serverMessage:str) -> Message:
        header = serverMessage.split(' ')[0]
        match header:
            case "ROOMLIST":
                roomlist = [room for room in serverMessage.split(' ')[1:]]
                return RoomList(roomlist)
            case "ROOMUSERLIST":
                roomusers = [user for user in serverMessage.split(' ')[1:]]
                return RoomUsersList(roomusers)
            case "ROOMMESSAGE":
                sender = serverMessage.split(' ').split(":")[0]
                roomname = serverMessage.split(' ').split(':')[1]
                messageBody = serverMessage.split(':')[2].strip()
                return RoomMessage(sender, roomname, messageBody)
            case "CHECKIN":
                return ServerCheckin()
            case _:
                raise Exception("recieved invalid server message: " + serverMessage)
        
    def executeServerMessage(self, serverMsg):
        match serverMsg:
            case RoomList(roomlist=roomlist):
                print("Available Rooms: ")
                for room in roomlist: print(room)
            case RoomUsersList(roomusers=roomusers):
                print("Users in room: ")
                for user in roomusers: print(user)
            case RoomMessage(sender=sender, roomname=roomname, messageBody=messageBody):
                print(f"message from {roomname}")
                print(sender + ": " + messageBody)
            case ServerCheckin():
                pass
            case _:
                raise Exception("execute server message recieved invalid server message: " + str(serverMsg))

    def readInput(self, s:socket):
        while not self.G_quit:
            usrMsg = input()
            if usrMsg[0]!="/":
                #catch invalid message early
                print("invalid user command")
                continue
            else:
                parsedCmd = self.parseUserCommand(usrMsg)
                match parsedCmd:
                    case Connect(host=host, port=port):
                        pass
                    case ListRooms():
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                    case JoinRoom(roomname=roomname):
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                        self.curRoom = roomname
                        self.rooms += [roomname]
                    case LeaveRoom(roomname=roomname):
                        if roomname not in self.rooms:
                            print("cannot leave room, not in room")
                            continue
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                        #wait for server response
                    case ListRoomUsers(roomname=roomname):
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                    case MessageRoom(roomname=roomname, messageBody=message):
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                    case Quit():
                        #send request to server
                        s.sendall(bytes(str(parsedCmd), 'utf-8'))
                        #wait for server ack
                        reply = self.getReply()
                        match reply:
                            case QuitAck():
                                print("disconnecting from server")
                                G_quit = True
                    case _:
                        #error in user command, send nothing, reprompt
                        print("invalid user command")
                        continue

if __name__ == '__main__':
    HOST, PORT = sys.argv[1], int(sys.argv[2])
    client = Client(HOST, PORT)
    client.run()
