from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import random

class Server(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.names = {}
        self.curr_coordinator = None

        self.file = open("text_1_1.txt", "w+")
        self.file.write("5\n")
        self.file.close()
        self.f1 = open("text_1_2.txt", "w+")
        self.f1.close()

    def datagramReceived (self, datagram, addr):
        datagram = datagram.decode('utf-8')
 
        if datagram.startswith("ready"):
            lst = datagram.split(":")
            self.names[lst[1]] = addr[1]
            self.clients.add(addr)
            print("\nNew client joined",addr[1])
            print("Current list of clients: ",", ".join(str(x) for _,x in self.clients))
            print(self.names)
            if len(self.clients) == 1 :
                self.transport.write(("make_coor").encode(), addr)
                self.curr_coordinator = addr
        
        elif datagram == "users":
            self.transport.write(", ".join(x for x in self.names.keys()).encode(), addr)        

        elif datagram.startswith("query"):
            lst = datagram.split(":")
            name = lst[1]
            port = self.names[name]
            self.transport.write(str(port).encode(), addr)

        elif datagram.startswith("get_clients"):
            self.transport.write(("clients_are",self.curr_coordinator,self.clients).encode(), addr)
        
        # not used for now                  
        elif datagram.startwith("coordinator_exist"):
            if self.curr_coordinator != None :
                self.transport.write(("coordinator_exist:1").encode(), addr)  
            else :
                self.transport.write(("coordinator_exist:0").encode(), addr)  

        elif datagram.startwith("change_coordinator"):
            msg = datagram.split(":") 
            port = (int)(msg[1])
            self.curr_coordinator = "127.0.0.1", port

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
            if addr == self.curr_coordinator :
                self.curr_coordinator = None
            print("\nClient left",addr[1])
            self.clients.remove(addr)
            self.names = {key:val for key, val in self.names.items() if val != addr[1]}
            print("Current list of clients: ","\n".join(str(x) for _,x in self.clients))
            print(self.names)
            

if __name__ ==  '__main__' :
    reactor.listenUDP(9999, Server())
    reactor.run()
