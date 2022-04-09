from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint

class Client(DatagramProtocol):
     def __init__ (self, host, port):
          if host == "localhost":
               host = "127.0.0.1"

          self.address = None
          self.id = host, port
          self.server = "127.0.0.1", 9999
          print("Working on id:", self.id)

     def startProtocol(self):
          self.transport.write("ready".encode("utf -8"), self.server)

     # def endProtocol(self):
     #      self.transport.write("end".encode("utf -8"), self.server)          
     
     def datagramReceived(self, datagram, addr):
          datagram = datagram.decode("utf-8")      
     
          if addr == self.server:
               print("Choose a client :")
               self.address = "127.0.0.1" , int(input("Write port: "))
               reactor.callInThread(self.send_message)
          else:
               print(addr, ":", datagram)
   
     def send_message(self):
          while True:
               ip = input("::: ") 
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
               else:
                    self.transport.write(ip.encode('utf-8'), self.address)

if __name__ == '__main__' :
     port = randint(1025, 7000)
     reactor.listenUDP(port, Client('localhost', port))
     reactor.run()