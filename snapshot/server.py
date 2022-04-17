from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor,task
import random
from threading import Thread
import time
import pickle

class Server(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.f1 = open("text_1_2.txt", "w+")
        self.f1.close()
        self.names = {}

    def datagramReceived (self, datagram, addr):
        datagram = datagram.decode('utf-8')
 
        if datagram.startswith("ready"):
            lst = datagram.split(":")
            self.names[lst[1]] = addr[1]
            self.clients.add(addr)
            print("\nNew client joined",addr[1])
            print("Current list of clients: ",", ".join(str(x) for _,x in self.clients))
            print(self.names)
        
        elif datagram == "users":
            self.transport.write(", ".join(x for x in self.names.keys()).encode(), addr)        

        elif datagram.startswith("query"):
            lst = datagram.split(":")
            name = lst[1]
            port = self.names[name]
            self.transport.write(str(port).encode(), addr)

        elif datagram.startswith("simulate"):
            lst = datagram.split(":")
            users = int(lst[1])
            f = open("text_1_2.txt", "a")
            f.write(str(users)+"\n")
            for i in range(1,51):
                sender = random.randint(0, users-1)
                receiver = random.randint(0, users-1)
                if(sender!=receiver):
                    f.write( "User" + str(sender)+" | "+  "User"+ str(receiver) + " | "+ "message" + str(i) + "\n")
                    s_addr = "127.0.0.1", self.names["User" + str(sender)]
                    to_port = self.names["User" + str(receiver)]
                    self.transport.write(("Simm:"+"User" + str(sender) + ":" + str(to_port) + ":message" + str(i)).encode(), s_addr)
                else:
                    f.write( "User" + str(sender) + " | " + "User" + str((receiver+1)%users) + " | " + "message" + str(i)+"\n")
                    s_addr = "127.0.0.1", self.names["User" + str(sender)]
                    to_port = self.names["User" + str((receiver+1)%users)]
                    self.transport.write(("Simm:" +"User" + str(sender) + ":" + str(to_port) + ":message" + str(i)).encode(), s_addr)
            f.close()
        
        elif datagram == "end":   
            print("\nClient left",addr[1])
            self.clients.remove(addr)
           # self.names.pop(self.names.keys()[list(self.names.values()).index(addr[1])])
            self.names = {key:val for key, val in self.names.items() if val != addr[1]}
            print("Current list of clients: ","\n".join(str(x) for _,x in self.clients))
            print(self.names)


def file_polling():
    last_dict = None
    with (open("snap_file.pkl", "rb")) as openfile:
        while True:
            try:
                last_dict = pickle.load(openfile)
            except EOFError:
                break
    if last_dict != None :
        if last_dict["Recieved at"] != "-" and time.time() - float(last_dict["Recieved at"]) > 2 :
            line = {"Communication Status" : "No communication", "Sent at" : "-", "Recieved at" : "-", "msg" : "-", "from" : "-", "to" : "-"}
            f = open("snap_file.pkl","wb")
            pickle.dump(line,f)
            f.close()


if __name__ ==  '__main__' :
    reactor.listenUDP(9999, Server())
    l = task.LoopingCall(file_polling)
    l.start(2)
    reactor.run()
