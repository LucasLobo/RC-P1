#!/usr/bin/env python3
import sys
import socket
import os.path
import datetime

from _thread import *
from os import path
from datetime import datetime

# Global Variables
USER_FILE = "./CentralServer/user_"
CS_IP = ""
CS_PORT = 58054
BUFFER_SIZE = 1024

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    global USER_FILE
    user = ""
    reply = ""
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = conn.recv(BUFFER_SIZE)

        if not data: 
            break
        else:
            message = data.decode()
            msg_split = message.split()
            
            try:
                if msg_split[0] == "AUT" and len(msg_split) == 3:
                    user = msg_split[1]
                    password = msg_split[2]
                
                    user_file = USER_FILE + user + ".txt"
                
                    if not path.exists(user_file):
                        os.makedirs(USER_FILE + user)
                        f = open(user_file,"w+")
                        f.write(password)
                        reply = "AUR NEW\n"
                        print("New user: " + user)
                    else:
                        f = open(user_file,"r")
                        stored_pass = f.read()
                        if stored_pass == password:
                            reply = "AUR OK\n"
                        else:
                            reply = "AUR NOK\n"
                elif msg_split[0] == "LSD" and len(msg_split) == 1:
                    len_dirs = len(os.listdir(USER_FILE + user))
                    if len_dirs != 0:
                        list_dirs = os.listdir(USER_FILE + user)
                        reply = "LDR " + str(len_dirs)
                        for i in range(len_dirs):
                            reply += " " + list_dirs[i]
                        reply += "\n"
                    else:
                        reply = "LDR 0\n"
                elif msg_split[0] == "DLU" and len(msg_split) == 1:
                    len_dirs = len(os.listdir(USER_FILE + user))
                    if len_dirs != 0:
                        reply = "DLR NOK\n"
                    else:
                        os.rmdir(USER_FILE + user)
                        os.remove(USER_FILE + user + ".txt")
                        reply = "DLR OK"
                else:
                    reply = "ERR\n"
            except IndexError:
                break
        conn.sendall(reply.encode())
     
    #came out of loop
    conn.close()

def central_server_init():
    #Variables
    global CS_IP
    global CS_PORT
    
    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #Get Host Name
    CS_IP = socket.gethostbyname(socket.gethostname())
    
    #Bind Socket to CS IP and CS PORT
    try:
        s.bind((CS_IP, CS_PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
     
    #Start listening on Socket
    s.listen(10)
    print('<<<Waiting for Connections>>>')
    
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,))
 
    s.close()

#Check if Central Server directory exists, if not it creates one
if not path.exists('CentralServer'):
    os.makedirs('CentralServer')

#Reading Console Commands from Sys
size_commands = len(sys.argv)

if size_commands > 1 and size_commands < 4:
    if size_commands == 3:
        if sys.argv[1] == "-p":
            try :
                CS_PORT = int(sys.argv[2])
            except ValueError:
                print("Invalid Port!")
            else:
                central_server_init()
        else:
            print("Invalid Command!")
    else:
        print("Invalid number of commands!")
else:
    central_server_init()
