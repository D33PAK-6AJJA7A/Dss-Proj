from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import socket     
from random import randint
import os
import time
 
connect_flag = 0      # to check if client have connected to any other online client for chatting
user_flag = 0         # to check if client has asked for list of online clients
recv_flag = 0         # to check if two way connection is established for chatting
coordinator_flag = 0  # to check if client is coordinator or not
alive_flag = 0        # to check if client is online or not
vote_flag = 0         # to check if client wants to be coordinator or not

class Client(DatagramProtocol):
     def __init__ (self, host, port):
          self.address = None                # address of client who has connected for chatting
          self.id = host, port               # address of current client
          self.server = "127.0.0.1", 9999  # address of server
          self.name = ""                     # name of current client
          self.other_user = ""               # name client who has connected for chatting
          self.curr_coordinator = None       # current coordinator
          self.curr_users = set()            # current online users
          print("Menu commands : ")
          print("__end__ : Stops communication and closes the client.")
          print("__users__ : To get a list of current online users.")
          print("__connect__ : To connect to other online user.")
          print("__simulate__ : To simulate random conversations.")
          print("__check__ : To check up on coordinator and to conduct conduct election if neccesary.")
          print("Working on id:", self.id)

     # takes name of client and stores it in a set
     def startProtocol(self):
          name = input("Name: ")
          self.name = name
          line = "ready:"+name
          self.transport.write(line.encode('utf -8'), self.server)
          reactor.callInThread(self.poll_connect)
     
     # function to conduct election when there is no coordinator
     def conduct_election(self):
          global vote_flag
          global alive_flag
          global coordinator_flag

          # gets all online clients and current coordinator
          self.transport.write(("get_clients").encode('utf -8'), self.server)
          time.sleep(2)
          
          # election not needed if coordinator is present 
          if self.curr_coordinator != None :
               print("No election needed ... coordinator alive")
               return 

          # get all clients with higher priority
          ports = set()
          flg = 0
          for x in self.curr_users:
              if x[1] > self.id[1]:
                  ports.add(x)

          # check all high priority clients for status
          for x in ports:
              to_addr = x
              self.transport.write(("u_alive_buddy").encode('utf -8'), to_addr)
              time.sleep(2)

              # if a high priority client is online 
              if alive_flag == 1:
                self.transport.write(("wanna_be_coordinator").encode('utf -8'), to_addr)
                time.sleep(2)

                # if that high priority client wants to be coordinator
                if vote_flag == 1:
                    self.transport.write(("change_coordinator:",str(x)).encode('utf -8'), self.server)
                    self.transport.write(("make_coor").encode('utf -8'), to_addr)

                    # announce victory of new assigned coordinator
                    curr_name = str(next((name for name, port in self.curr_users.items() if port == x), None))
                    for y in self.curr_users:
                         del_addr = y
                         if y[1] != x[1] :
                              self.transport.write(("del_coor").encode('utf -8'), del_addr)
                         if y[1] < x[1] :
                              self.transport.write(("announce_victory:" + curr_name).encode('utf -8'), del_addr)
                    flg = 1
                    break
 
          # if no high priority coordinator is present, make current client as coordinator and announce victory
          if flg == 0 :
            coordinator_flag = 1
            self.transport.write(( "change_coordinator:"+str(self.id) ).encode('utf-8'), self.server)
            for y in self.curr_users:
               del_addr = y
               if y[1] != self.id[1] :
                    self.transport.write(("del_coor").encode('utf -8'), del_addr)
               if y[1] < self.id[1] :
                    self.transport.write(("announce_victory:" + self.name).encode('utf -8'), del_addr)
                    
            print("\n You are elected as coordinator \n")


     # function to explore all menu commands
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
               
               elif ip == "__end__" :
                   coordinator_flag = 0
                   self.transport.write("end".encode('utf-8'), self.server)
                   reactor.stop()
                   os._exit(0)

               elif ip == "__check__" :
                    if coordinator_flag == 1 : 
                        print("You are coordinator idiot .. ")
                    else :
                        reactor.callInThread(self.conduct_election)

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
          global coordinator_flag
          global vote_flag
          global alive_flag

          datagram = datagram.decode('utf-8')   

          # to make current client as coordinator
          if datagram.startswith("make_coor"):
              coordinator_flag = 1
              print("\n You are elected as coordinator \n")

          # to delete current client as coordinator
          elif datagram.startswith("del_coor"):
              coordinator_flag = 0
          
          # to announce victory of elected coordinator
          elif datagram.startswith("announce_victory") :
               msg = datagram.split(":")
               print(msg[1] + " is elected as new coordinator \n")

          # to check if current client is online
          elif datagram.startswith("u_alive_buddy"):
              self.transport.write(("res_alive:" + str(randint(1,101)%2)).encode('utf-8'), addr) 

          # to check if current client wants to be coordinator
          elif datagram.startswith("wanna_be_coordinator"):
              self.transport.write(("res_coor:" + str(randint(1,101)%2)).encode('utf-8'), addr) 
          
          # to respond if current client is alive
          elif datagram.startswith("res_alive"):
               msg = datagram.split(":")
               alive_flag = int(msg[1])

          # to respond if current client wants to be coordinator
          elif datagram.startswith("res_coor"):
               msg = datagram.split(":")
               vote_flag = int(msg[1])
          
          # to store online clients and current coordinator 
          elif datagram.startswith("clients_are|") :
               msg = datagram.split("|")
               if msg[1] == "None" :
                    self.curr_coordinator = None
               else :
                    temp_lst = msg[1].strip('(').strip(')').split(",")
                    adddd = str(temp_lst[0].strip('\'').strip('\''))
                    self.curr_coordinator = adddd, int(temp_lst[1])
               temp_set = set(msg[2].split('&')) 
               self.curr_users = set()
               for x in temp_set:
                    temp_lst = x.strip('(').strip(')').split(",")
                    adddd = str(temp_lst[0].strip('\'').strip('\''))
                    t = adddd, int(temp_lst[1])
                    self.curr_users.add(t)

          # to send a simulated message 
          elif datagram.startswith("Simm:"):
               lib = datagram.split(":")
               from_name = lib[1]
               ip = lib[3]
               temp_lst = lib[2].strip('(').strip(')').split(",")
               adddd = str(temp_lst[0].strip('\'').strip('\''))
               to_addr = adddd, int(temp_lst[1])
               print("--> ", ip, " : ", lib[4])
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
               msg = datagram.split(":")
               addrr = msg[0]
               port = int(msg[1])
               self.address = addrr, port
               reactor.callInThread(self.send_message)
          else:
               # announce if connection is lost
               if datagram == "__end__":
                    print(self.other_user+" has ended the conversation")
                    self.transport.write("end".encode('utf-8'), self.server)
                    reactor.stop()
                    os._exit(0)
               
               # to recieve all online clients names
               if user_flag == 1:
                    user_flag = 0
                    print("Users: ",datagram)
               
               # to recieve a chat and to store it in a file
               elif recv_flag == 1 and datagram.startswith("|msg|") :
                    tot = datagram.split(":")
                    msg = tot[2]
                    tim = tot[1]
                    print(self.other_user, " : ", msg)
                    file = open("text_1_1.txt", "a")
                    line = "Sent at : " + tim + ", Recieved at : " + str(time.time()) +" , msg : " + msg + " , from "+self.name+ " to " +self.other_user+"\n"
                    file.write(line)
                    file.close()
   
     # function for chatting with other clients
     def send_message(self):
          global coordinator_flag
          while True:
               ip = input("--> ") 

               # to end a conversation
               if(ip == "__end__"): 
                    self.transport.write("end".encode('utf-8'), self.server)
                    self.transport.write("__end__".encode('utf-8'), self.address)
                    coordinator_flag = 0
                    reactor.stop()
                    os._exit(0)

               # to get all online users
               elif(ip == "__users__"):
                    self.transport.write("users".encode('utf-8'), self.server)
               
               # to send a chat to connected client
               else:
                    self.transport.write(("|msg|:"+str(time.time()) + ":" + ip).encode('utf-8'), self.address)

# client is assigned a random port to communicate
if __name__ == '__main__' :
     port = randint(1025, 7000)
     reactor.listenUDP(port, Client(str(socket.gethostbyname(socket.gethostname())), port))
     reactor.run()