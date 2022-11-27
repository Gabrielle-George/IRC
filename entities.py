#example code taken from RealPython socket tutorial
import selectors
import socket
import types
import IRCparse


class Server(object):

    def __init__(self, name):
        self.name = name
        self.userList = {}
        self.roomList = {}
        #self.conn_list = [] #temporary
        self.sel = None
        self.tmpListOfNames = ["Galadriel", "Elrond", "Frodo", "Gilgalad" ]
        self.tmpID = 0;
        self.cmds = IRCparse.IRCcommands()

    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        #self.conn_list.append([(conn, addr), self.usrID])
        self.addUser(conn, addr, self.tmpListOfNames[self.tmpID])
        self.tmpID +=1

    def parseCmd(self, incoming_cmd, fd):
        #compares incoming_cmd to cmd_list, if match returns, calls function with ongoing parameters in incoming_cmd
        #returns false if no recognized command is issued
        #payload, fd, userList
        print('incoming_cmd is ', incoming_cmd)
        parsedType, payload = IRCparse.parse(incoming_cmd)
        # print("parsedtype:", parsedType, "payload,", payload)
        print('self.cmds is', self.cmds)
        if parsedType == self.cmds.DEFAULT:
            self.do_sendToAllInList(payload, fd, self.userList)
        if parsedType == self.cmds.JOINROOM:
            self.do_userJoinRoom(payload,fd)

    def service_connection(self,key, mask):
        sock = key.fileobj
        data = key.data
        #global usrID #this is the second instatitaion of this globally, possibly dangerous?
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            else:
                print(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                self.parseCmd(data.outb.decode('utf-8'), sock.fileno())
                data.outb = b'' #flush the buffer?


    def startServer(self, host, port): 
        self.sel = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
    """
    create a new room object, add it to the room list
    """
    def do_userJoinRoom(self, roomName, fd):
        if roomName not in self.roomList.keys():
            print("creating room " + roomName)
            self.createRoom(roomName)
        (self.roomList[roomName]).addUsertoRoom(fd)
        print("adding user" + self.userList[fd].nick +" to " +roomName)


    def createRoom(self,roomName):
        newRoom = Room(roomName)
        self.roomList[roomName] = newRoom


    #returns a 0 for success, -1 for fail
    #todo: can't actually add nicks.  Just do it for ease of testing.
    def addUser(self,sock, addr,nickname = None):
        fd = sock.fileno()
        if fd in self.userList:
            return -1 #TODO then kick them
        self.userList[fd] = User(fd, sock, addr, nickname)

    #parsed commands here?
    def do_sendToAllInList(self,payload, fd, userList):
        sender = self.userList[fd]
        message = sender.nick + ": " + payload
        messageToSend = bytes("{}".format(message),"utf-8")
        print("sending:" + messageToSend.decode("utf-8"))
        print(userList)
        for fd in userList.keys():
            print(fd)
            sent = userList[fd].sock.send(messageToSend)
        return sent


 
"""    def listRooms(user):
        return []"""

"""    def doesNickExist(newNick):
        for user in userList:
            if user"""
        
"""
class represents a room on the server
"""        
class Room(object):

    def __init__(self, name):
        self.name = name
        self.userList = []

    def addUsertoRoom(self,fd):
        if fd not in self.userList:
            self.userList.append(fd)


            

class User(object):
    #todo: can't actually add nicks.  Just do it for testing.
    def __init__(self, fd, usrSock, addr, nickname = None):
        self.completedHandshake = False
        self.nick = nickname
        self.fd = fd
        self.addr = addr
        self.roomList = [] #can we get around this? idk.
        self.sock = usrSock

    def setNick(self,nickname):
        self.nick = nickname

    """
    def joinRoom(self, roomName):
        #send message to server asking to join room
        self.roomList.append(roomName)
    """