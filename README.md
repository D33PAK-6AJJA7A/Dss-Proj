# Distributed System Course Project

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)  	![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

A P2P based discributed chat system written in twisted python. In addition implemented distributed computing control algorithms namely Bully leader election algorithm and Chandy-Lamport Global snapshot algorithm.

## HOW TO RUN
 - Go to the “bully” folder to execute the Bully algorithm for leader election or to the “snapshot” folder to execute the Global snapshot algorithm.
 - Run server.py file on a terminal with command : “python3 server.py”.
 - Run client.py file on a seperate terminal with command : “python3 client.py”.
 - Enter a name for your client.
 - Try any executable command shown above. 

Note :
 - To view all the chats till now open the “text_1_1.txt” file which is created in the same folder. 
 - To view all the simulated chats open the “text_1_2.txt” file which is created in the same folder. 

## FAQ
Q. What is the proper use of "__connect__" command ?
A. “__connect__” command should be executed by both the clients who want to chat with each other and enter each other’s name to chat.

Q. What is the proper use of "__simulate__" command ? 
 - For working of “__simulate__” command clients with names as User0, User1, User2 so on upto (entered users - 1) should be running in order to simulate random chats  - between them.


