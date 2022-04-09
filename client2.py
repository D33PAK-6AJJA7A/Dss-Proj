from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import sys
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
          print("Working on id:", self.id,"\n")
          
     def startProtocol(self) :
          self.transport.write("ready".encode("utf -8"), self.server)
          while True:
               ip = input("--> ") 
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
                    reactor.stop()
                    os._exit(0)
               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
                    # print(datagram.decode("utf-8"))
               elif(ip == "__connect__"):
                    self.address = "127.0.0.1" , int(input("Choose a client : "))
                    break
          
          reactor.callInThread(self.send_message)

      
     
     def datagramReceived(self, datagram, addr):     
          print("hi")
          #datagram = datagram.decode('utf-8')
          print(datagram.decode('utf-8'))
          return
          # if addr == self.server:
          #      self.address = "127.0.0.1" , int(input("Choose a client : "))
          #      reactor.callInThread(self.send_message)
          # else:
          #      print(addr[1], ":", datagram)

          

     def send_message(self):
          while True:
               ip = input("--> ") 
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
                    reactor.stop()
                    os._exit(0)
               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
                    # datagram = datagram.decode("utf-8") 
                    # print(datagram)
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