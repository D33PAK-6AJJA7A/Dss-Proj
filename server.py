from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Server(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.file = open("text_1_1.txt", "w+")
        self.file.write("5\n")
        self.file.close()
        self.names = {}

    def datagramReceived (self, datagram, addr):
        datagram = datagram.decode( "utf-8")

        if datagram.startswith("ready"):
            lst = datagram.split(":")
            self.names[lst[1]] = addr[1]
            self.clients.add(addr)
            print("\nNew client joined",addr[1])
            print("Current list of clients: ",", ".join(str(x) for _,x in self.clients))
            print(self.names)
            # self.transport.write("\n".join(str(x) for x in self.clients).encode(), addr)
        
        elif datagram == "users":
            self.transport.write(", ".join(x for x in self.names.keys()).encode(), addr)        

        elif datagram.startswith("query"):
            lst = datagram.split(":")
            name = lst[1]
            port = self.names[name]
            self.transport.write(str(port).encode(), addr)
        
        elif datagram == "end":   
            print("\nClient left",addr[1])
            self.clients.remove(addr)
            self.names.pop(self.names.keys()[list(self.names.values()).index(addr[1])])
            print("Current list of clients: ","\n".join(str(x) for _,x in self.clients))
            print(self.names)
            

if __name__ ==  '__main__' :
    reactor.listenUDP(9999, Server())
    reactor.run()
