from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import os
import time
import pickle

connect_flag = 0      # to check if client have connected to any other online client for chatting
user_flag = 0         # to check if client has asked for list of online clients
recv_flag = 0         # to check if two way connection is established for chatting

class Client(DatagramProtocol):
     def __init__ (self, host, port):
          if host == "localhost":
               host = "127.0.0.1" 

          self.address = None                # address of client who has connected for chatting
          self.id = host, port               # address of current client
          self.server = "127.0.0.1", 9999    # address of server
          self.name = ""                     # name of current client
          self.other_user = ""               # name client who has connected for chatting
          print("Menu commands : ")
          print("__end__ : Stops communication and closes the client")
          print("__users__ : To get a list of current online users")
          print("__connect__ : To connect to other online user")
          print("__simulate__ : To simulate random conversations")
          print("__snapshot__ : Retrieves latest global snapshot")
          print("Working on id:", self.id)

     # takes name of client and stores it in a set
     def startProtocol(self):
          name = input("Name: ")
          self.name = name
          line = "ready:"+name
          self.transport.write(line.encode('utf -8'), self.server)
          reactor.callInThread(self.poll_connect)
     
     # function to explore all menu commands
     def poll_connect(self):
          global connect_flag
          global user_flag
          global recv_flag

          while True:
               ip = input("Enter menu command: ")
               if ip == "__users__":
                    user_flag = 1
                    self.transport.write("users".encode('utf -8'), self.server)
                    time.sleep(1)
               elif ip == "__simulate__" :
                    users = int(input("Enter no. of users to chat : "))
                    line = "simulate:"+str(users)
                    self.transport.write(line.encode('utf -8'), self.server)

               elif ip == "__snapshot__" :
                   reactor.callInThread(self.file_polling)

               elif ip == "__end__" :
                   reactor.stop()
                   os._exit(0)

               elif ip == "__connect__":
                    name = input("Enter name of user: ")
                    self.other_user = name
                    line = "query:"+name
                    connect_flag = 1
                    recv_flag = 1
                    self.transport.write(line.encode('utf -8'), self.server)
                    break
               
               else:
                   print("Enter mentioned command.")
          
          self.transport.write("users".encode('utf -8'), self.server) 
     
     # all packets recieved by this client arrives at this function
     def datagramReceived(self, datagram, addr):
          global connect_flag
          global user_flag
          global recv_flag
          datagram = datagram.decode('utf-8')      

          # to send a simulated message 
          if datagram.startswith("Simm:"):
               lib = datagram.split(":")
               from_name = lib[1]
               to_port = int(lib[2])
               ip = lib[3]
               to_addr = "127.0.0.1", to_port
               print("--> ", ip, " : ", to_port)
               self.transport.write(("Simm_recv:" + from_name +":" + ip).encode('utf-8'), to_addr)

          # to recieve a simulated message
          elif datagram.startswith("Simm_recv"):
               tot = datagram.split(":")
               msg = tot[2]
               name = tot[1]
               print(name, " : ", msg)

          # if client is connected to other client, then client ready to send messages
          if connect_flag == 1:
               connect_flag = 0
               port = int(datagram)
               self.address = "127.0.0.1" , port
               reactor.callInThread(self.send_message)
          else:
               # announce if connection is lost
               if datagram == "__end__":
                    print(self.other_user+" has ended the conversation")
                    reactor.stop()
                    os._exit(0)
               
               # to recieve all online clients names
               if user_flag == 1:
                    user_flag = 0
                    print("Users: ",datagram)

               # to recieve a chat and to store it in a file as current snapshot
               elif recv_flag == 1 and datagram.startswith("|msg|") :
                    tot = datagram.split(":")
                    msg = tot[2]
                    tim = tot[1]
                    print(self.other_user, " : ", msg)
                    line = {"Communication Status" : "successfully recieved", "Sent at" : tim, "Recieved at" : str(time.time()), "msg" : msg, "from" : self.other_user, "to" : self.name}
                    f = open("snap_file.pkl","wb")
                    pickle.dump(line,f)
                    f.close()
   
   # function for chatting with other clients
     def send_message(self):
          while True:
               ip = input("--> ") 

               # to end a conversation
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
                    self.transport.write("__end__".encode('utf-8'), self.address)
                    reactor.stop()
                    os._exit(0)

               # to get all online users
               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
                
               # to get latest global snapshot
               elif ip == "__snapshot__" :
                   reactor.callInThread(self.file_polling)

               # to send a chat to connected client and to store it in a file as current snapshot
               else:
                    line = {"Communication Status" : "On the way", "Sent at" : str(time.time()), "Recieved at" : "-", "msg" : ip, "from" : self.name, "to" : self.other_user}
                    f = open("snap_file.pkl","wb")
                    pickle.dump(line,f)
                    f.close()
                    self.transport.write(("|msg|:"+str(time.time()) + ":" + ip).encode('utf-8'), self.address)

     # function to print latest global snapshot
     def file_polling(self):
        last_dict = None
        with (open("snap_file.pkl", "rb")) as openfile:
            while True:
                try:
                    last_dict = pickle.load(openfile)
                except EOFError:
                    break
        if last_dict != None :
            print(last_dict)
            print()
        else:
            print("No Communication yet. \n")

# client is assigned a random port to communicate
if __name__ == '__main__' :
     port = randint(1025, 7000)
     reactor.listenUDP(port, Client('localhost', port))
     reactor.run()