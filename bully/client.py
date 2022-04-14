from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import os
import time


connect_flag = 0
user_flag = 0
recv_flag = 0
coordinator_flag = 0
alive_flag = 0
vote_flag = 0

class Client(DatagramProtocol):
     def __init__ (self, host, port):
          if host == "localhost":
               host = "127.0.0.1" 

          self.address = None
          self.id = host, port
          self.server = "127.0.0.1", 9999
          self.name = ""
          self.other_user = ""
          self.curr_coordinator = None
          self.curr_users = set()
          print("Menu commands : ")
          print("__end__ : Stops communication and closes the client.")
          print("__users__ : To get a list of current online users.")
          print("__connect__ : To connect to other online user.")
          print("__chats__ : To get all previous chats.")
          print("__simulate__ : To sumulate random conversations.")
          print("__check__ : To check up on coordinator.")
          print("Working on id:", self.id)

     def startProtocol(self):
          name = input("Name: ")
          self.name = name
          line = "ready:"+name
          self.transport.write(line.encode('utf -8'), self.server)
          reactor.callInThread(self.poll_connect)
     
     def conduct_election(self):
          global vote_flag
          global alive_flag
          global coordinator_flag

          self.transport.write(("get_clients").encode('utf -8'), self.server)
          time.sleep(2)
          
          if self.curr_coordinator != None :
               print("No election needed ... coordinator alive")
               return 

          ports = set()
          flg = 0
          for x in self.curr_users:
              if x[1] > self.address[1]:
                  ports.add(x[1])
          for x in ports:
              to_addr = "127.0.0.1",x
              self.transport.write(("u_alive_buddy").encode('utf -8'), to_addr)
              time.sleep(2)
              if alive_flag == 1:
                self.transport.write(("wanna_be_coordinator").encode('utf -8'), to_addr)
                time.sleep(2)
                if vote_flag == 1:
                    self.transport.write(("change_coordinator:",str(x)).encode('utf -8'), self.server)
                    self.transport.write(("make_coor").encode('utf -8'), to_addr)
                    flg = 1
                    break

          if flg == 0 :
            coordinator_flag = 1
            self.transport.write(("change_coordinator:",str(self.address[1])).encode('utf -8'), self.server)
            print("\n You are elected as coordinator \n")


     def poll_connect(self):
          global connect_flag
          global user_flag
          global recv_flag
          global coordinator_flag
          global vote_flag
          global alive_flag

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

               elif ip == "__check__" :
                    if coordinator_flag == 1 : 
                        print("You are coordinator idiot .. ")
                    else :
                        reactor.callInThread(self.conduct_election)

               elif ip == "__connect__":
                    connect_flag = 1
                    recv_flag = 1
                    name = input("Enter name of user: ")
                    self.other_user = name
                    line = "query:"+name
                    self.transport.write(line.encode('utf -8'), self.server)
                    break
          
          self.transport.write("users".encode('utf -8'), self.server)    
     
     def datagramReceived(self, datagram, addr):

          global connect_flag
          global user_flag
          global recv_flag
          global coordinator_flag
          global vote_flag
          global alive_flag

          datagram = datagram.decode('utf-8')      

          if datagram.startswith("make_coor"):
              coordinator_flag = 1
              print("\n You are elected as coordinator \n")

          elif datagram.startswith("u_alive_buddy"):
              self.transport.write(("res_alive" + str(randint(1,101)%2)).encode('utf-8'), addr) 

          elif datagram.startswith("wanna_be_coordinator"):
              self.transport.write(("res_coor" + str(randint(1,101)%2)).encode('utf-8'), addr) 
          
          elif datagram.startswith("res_alive"):
              alive_flag = 1

          elif datagram.startswith("res_coor"):
              vote_flag = 1
          
          elif datagram[0] == "clients_are" :
               self.curr_coordinator = datagram[1]
               self.curr_users = datagram[2]

          elif datagram.startswith("Simm:"):
               # print(datagram)
               lib = datagram.split(":")
               from_name = lib[1]
               to_port = int(lib[2])
               ip = lib[3]
               to_addr = "127.0.0.1", to_port
               print("--> ", ip, " : ", to_port)
               self.transport.write(("Simm_recv:" + from_name +":" + ip).encode('utf-8'), to_addr)

          elif datagram.startswith("Simm_recv"):
               tot = datagram.split(":")
               msg = tot[2]
               name = tot[1]
               print(name, " : ", msg)

          if connect_flag == 1:
               connect_flag = 0
               port = int(datagram)
               self.address = "127.0.0.1" , port
               reactor.callInThread(self.send_message)
          else:
               if datagram == "__end__":
                    print(self.other_user+" has ended the conversation")
                    reactor.stop()
                    os._exit(0)
               
               if user_flag == 1:
                    user_flag = 0
                    print("Users: ",datagram)
               elif recv_flag == 1 and datagram.startswith("|msg|") :
                    tot = datagram.split(":")
                    msg = tot[2]
                    tim = tot[1]
                    print(self.other_user, " : ", msg)
                    file = open("text_1_1.txt", "a")
                    line = "Sent at : " + tim + ", Recieved at : " + str(time.time()) +" , msg : " + msg + " , from "+self.name+ " to " +self.other_user+"\n"
                    file.write(line)
                    file.close()
   
     def send_message(self):
          global coordinator_flag
          while True:
               ip = input("--> ") 
               if(ip == "__end__"):
                    self.transport.write("end".encode('utf-8'), self.server)
                    self.transport.write("__end__".encode('utf-8'), self.address)
                    coordinator_flag = 0
                    reactor.stop()
                    os._exit(0)

               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
               else:
                    self.transport.write(("|msg|:"+str(time.time()) + ":" + ip).encode('utf-8'), self.address)

if __name__ == '__main__' :
     port = randint(1025, 7000)
     reactor.listenUDP(port, Client('localhost', port))
     reactor.run()