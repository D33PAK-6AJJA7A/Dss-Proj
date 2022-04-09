import random

def text_file_generator(users, pathfile):
  f = open(pathfile, "w")
  f.write(str(users)+"\n")
  for i in range(1,51):
    sender = random.randint(0, users-1)
    receiver = random.randint(0, users-1)
    if(sender!=receiver):
      f.write( "User" + str(sender)+"|"+  "User"+ str(receiver) + "|"+ "message" + str(i) + "\n")
    else:
      f.write( "User" + str(sender) + "|" + "User" + str((receiver+1)%users) + "|" + "message" + str(i)+"\n")
  f.close()

text_file_generator(3,"text_1_2.txt")