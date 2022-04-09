from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Server(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.file = open("text_1_1.txt", "w+")
        self.file.write("5\n")
        self.file.close()
    
    def datagramReceived (self, datagram, addr):
        datagram = datagram.decode( "utf-8")

        if datagram == "ready":
            self.clients.add(addr)
            print("\nNew client joined",addr[1])
            print("Current list of clients: ",", ".join(str(x) for _,x in self.clients))
            # self.transport.write("\n".join(str(x) for x in self.clients).encode(), addr)

        elif datagram == "users":
            self.transport.write("\n".join(str(x) for _,x in self.clients).encode(), addr)
        
        elif datagram == "end":   
            print("\nClient left",addr[1])
            self.clients.remove(addr)
            print("Current list of clients: ","\n".join(str(x) for _,x in self.clients))
            

if __name__ ==  '__main__' :
    reactor.listenUDP(9999, Server())
    reactor.run()
