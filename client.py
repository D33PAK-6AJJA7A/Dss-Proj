from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import os

class Client(DatagramProtocol):
     def __init__ (self, host, port):
          if host == "localhost":
               host = "127.0.0.1"

          self.address = None
          self.id = host, port
          self.server = "127.0.0.1", 9999
          print("Instructions : ")
          print("__end__ : Stops communication and closes the client")
          print("__users__ : To get a list of current online users")
          print("__connect__ : To connect to other online user")
          print("Working on id:", self.id)

     def startProtocol(self):
          self.transport.write("ready".encode("utf -8"), self.server)

     # def endProtocol(self):
     #      self.transport.write("end".encode("utf -8"), self.server)          
     
     def datagramReceived(self, datagram, addr):
          # print("hi")
          datagram = datagram.decode("utf-8")      
     
          if addr == self.server:
               print("Choose a client :")
               self.address = "127.0.0.1" , int(input("Write port: "))
               reactor.callInThread(self.send_message)
          else:
               if datagram == "__end__":
                    print("User has ended conversation")
                    reactor.stop()
                    os._exit(0)
               print(addr, ":", datagram)
               print("\n-->",end="")
   
     def send_message(self):
          print("-->",end="")
          while True:
               ip = input("") 
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
                    self.transport.write("__end__".encode('utf-8'), self.address)
                    reactor.stop()
                    os._exit(0)

               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
               else:
                    self.transport.write(ip.encode('utf-8'), self.address)
                    file = open("text_1_1.txt", "a")
                    #from user1837 to user28372 :::: message
                    line = "from user"+str(self.id[1]) + " to user" + str(self.address[1]) + " :::: "+str(ip)+"\n"
                    file.write(line)
                    file.close()

if __name__ == '__main__' :
     port = randint(1025, 7000)
     reactor.listenUDP(port, Client('localhost', port))
     reactor.run()