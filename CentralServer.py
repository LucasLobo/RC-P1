#!/usr/bin/env python3
import sys
import os
import socket
import os.path
import random
import shutil

from _thread import *
from os import path

# Global Variables
USER_FILE = "./CentralServer/user_"
CS_IP = ""
CS_PORT = 58054
BUFFER_SIZE = 1024
BS_FILE = "./CentralServer/BS_LIST.txt"

#Function for handling UDP connections. This will be used to create threads
def client_udp_thread(sock,data,addr):
    reply = ""
    
    message = data.decode()
    msg_split = message.split()
    
    if msg_split[0] == "REG" and len(msg_split) == 3:
        try :
            BS_port = int(msg_split[2])
            if not path.exists(BS_FILE):
                f = open(BS_FILE,"w+")
                f.write(msg_split[1] + "," + msg_split[2] + ";")
                f.close()
                print("+BS: " + msg_split[1] + " " + msg_split[2])
                reply = "RGR OK\n"
            else:
                f = open(BS_FILE,"r")
                stored_bs = f.read()
                f.close()
                bs_list = stored_bs.split(";")
                bs_word = msg_split[1] + "," + msg_split[2]
                if bs_word in bs_list:
                    reply = "RGR NOK\n"
                else:
                    f = open(BS_FILE,"a")
                    f.write(msg_split[1] + "," + msg_split[2] + ";")
                    f.close()
                    print("+BS: " + msg_split[1] + " " + msg_split[2])
                    reply = "RGR OK\n"
        except ValueError:
            reply = "RGR ERR\n"
    elif msg_split[0] == "UNR" and len(msg_split) == 3:
        try:
            BS_port = int(msg_split[2])
            BS_ip = msg_split[1]
            
            f = open(BS_FILE,"r")
            stored_bs = f.read()
            f.close()
            
            bs_word = BS_ip + "," + str(BS_port)
            stored_bs_split = stored_bs.split(";")
            
            if bs_word in stored_bs_split:
                stored_bs_split.remove(bs_word)
                new_bs_info = ""
                
                if len(stored_bs_split) > 0:
                    for i in range(len(stored_bs_split)):
                        new_bs_info += stored_bs_split[i] + ";"
                
                f = open(BS_FILE,"w+")
                f.write(new_bs_info)
                f.close
                
                print("-BS: " + msg_split[1] + " " + msg_split[2])
                reply = "UAR OK\n"
            else:
                reply = "UAR NOK\n"
        except ValueError:
            reply = "UAR ERR\n"
    else:
        reply = "ERR\n"
    
    sock.sendto(reply.encode() , addr)
     

#Function for handling TCP connections. This will be used to create threads
def client_tcp_thread(conn):
    global USER_FILE
    user = ""
    password = ""
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
                        f.close()
                        reply = "AUR NEW\n"
                        print("New user: " + user)
                    else:
                        f = open(user_file,"r")
                        stored_pass = f.read()
                        f.close()
                        if stored_pass == password:
                            reply = "AUR OK\n"
                        else:
                            reply = "AUR NOK\n"
                elif msg_split[0] == "LSD" and len(msg_split) == 1:
                    print("User: " + user + "\tCommand: List Directories")
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
                    print("User: " + user + "\tCommand: Delete User")
                    len_dirs = len(os.listdir(USER_FILE + user))
                    if len_dirs != 0:
                        reply = "DLR NOK\n"
                    else:
                        os.rmdir(USER_FILE + user)
                        os.remove(USER_FILE + user + ".txt")
                        print("User " + user + " deleted")
                        reply = "DLR OK\n"
                elif msg_split[0] == "BCK":
                    print("User: " + user + "\tCommand: Backup Directory")
                    
                    data2 = conn.recv(BUFFER_SIZE)
                    message2 = data2.decode()
                    msg_split2 = message2.split()
                    
                    number_files = int(msg_split2[1])
                    if (len(msg_split2) - 2) == (number_files * 4):
                        directory_name = msg_split2[0]
                        directory_path = USER_FILE + user + "/" + directory_name
                        bs_file_dir = directory_path + "/" + "BS.txt"
                        if not path.exists(directory_path):
                            os.makedirs(directory_path)
                        
                            #Open BS Database file
                            f = open(BS_FILE,"r")
                            stored_bs = f.read()
                            f.close()
                            
                            #Get One BS
                            bs_list = stored_bs.split(";")
                            chosen_bs = bs_list[random.randint(0,len(bs_list)-2)]
                            bs_split = chosen_bs.split(",")
                            bs_ip = bs_split[0]
                            bs_port = int(bs_split[1])
                        
                            #Create BS file in dir
                            f = open(bs_file_dir,"w+")
                            f.write(chosen_bs)
                            f.close()
                            
                            udp_message = "LSU " + user + " " + password + "\n"
                            
                            # Send and receive BS message
                            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                            sock.sendto(udp_message.encode(), (bs_ip, bs_port))
                            
                            data, server = sock.recvfrom(BUFFER_SIZE)
                            bs_message = data.decode()
                            
                            sock.close()
                            #Check BS response
                            bs_message_split = bs_message.split()
                            if bs_message_split[0] == "LUR" and bs_message_split[1] == "OK":
                                reply = "BKR " + bs_ip + " " + str(bs_port) + " " + str(number_files)
                                i = 2
                                for i in range(len(msg_split2)):
                                    reply += " " + msg_split2[i]
                                reply += "\n"
                            else:
                                reply = "BKR EOF\n"
                        else:
                            #Open BS file in dir
                            f = open(bs_file_dir,"r")
                            stored_bs = f.read()
                            f.close()
                            
                            #Get BS
                            bs_split = stored_bs.split(",")
                            bs_ip = bs_split[0]
                            bs_port = int(bs_split[1])
                            
                            udp_message = "LSF " + user + " " + directory_name + "\n"
                            
                            # Send and receive BS message
                            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                            sock.sendto(udp_message.encode(), (bs_ip, bs_port))
                            
                            data, server = sock.recvfrom(BUFFER_SIZE)
                            bs_message = data.decode()
                            
                            sock.close()
                            #Check BS response
                            bs_message_split = bs_message.split()
                            if bs_message_split[0] == "LFD":
                                reply = "BKR " + bs_ip + " " + str(bs_port) + " " + bs_message_split[1]
                                i = 2
                                for i in range(len(bs_message_split)):
                                    reply += " " + bs_message_split[i]
                                reply += "\n"
                            else:
                                reply = "BKR EOF\n"
                    else:
                        reply = "BKR ERR\n"
                elif msg_split[0] == "LSF" and len(msg_split) == 2:
                    print("User: " + user + "\tCommand: List Directory Files")
                    directory_name = msg_split[1]
                    directory_path = USER_FILE + user + "/" + directory_name
                    bs_file_dir = directory_path + "/" + "BS.txt"
                    
                    if not path.exists(directory_path):
                        reply = "LFD NOK\n"
                    else:
                        #Open BS file in dir
                        udp_message = "LSF " + user + " " + directory_name + "\n"
                            
                        # Send and receive BS message
                        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        sock.sendto(udp_message.encode(), (bs_ip, bs_port))
                            
                        data, server = sock.recvfrom(BUFFER_SIZE)
                        bs_message = data.decode()
                        
                        sock.close()
                        #Check BS response
                        bs_message_split = bs_message.split()
                        if bs_message_split[0] == "LFD":
                            reply = "LFD " + bs_ip + " " + str(bs_port) + " " + bs_message_split[1]
                            i = 3
                            for i in range(len(bs_message_split)):
                                reply += " " + msg_split[i]
                            reply += "\n"
                        else:
                            reply = "LFD NOK\n"
                elif msg_split[0] == "RST":
                    print("User: " + user + "\tCommand: Restore Directory")
                    if len(msg_split) == 2:
                        directory_name = msg_split[1]
                        directory_path = USER_FILE + user + "/" + directory_name
                        bs_file_dir = directory_path + "/" + "BS.txt"
                        
                        if not path.exists(directory_path):
                            reply = "RSR EOF\n"
                        else:
                            #Open BS file in dir
                            f = open(bs_file_dir,"r")
                            stored_bs = f.read()
                            f.close()
                            
                            #Get BS
                            bs_split = stored_bs.split(",")
                            bs_ip = bs_split[0]
                            bs_port = int(bs_split[1])
                                
                            reply = "RSR " + bs_ip + " " + bs_port + "\n"
                    else:
                        reply = "RSR ERR\n"
                elif msg_split[0] == "DEL" and len(msg_split) == 2:
                    print("User: " + user + "\tCommand: Delete Directory")
                    directory_name = msg_split[1]
                    directory_path = USER_FILE + user + "/" + directory_name
                    bs_file_dir = directory_path + "/" + "BS.txt"
                    
                    if not path.exists(directory_path):
                        reply = "DDR NOK\n"
                    else:
                        #Open BS file in dir
                        f = open(bs_file_dir,"r")
                        stored_bs = f.read()
                        f.close()
                            
                        #Get BS
                        bs_split = stored_bs.split(",")
                        bs_ip = bs_split[0]
                        bs_port = int(bs_split[1])
                        
                        udp_message = "DLB " + user + " " + directory_name + "\n"
                            
                        # Send and receive BS message
                        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                        sock.sendto(udp_message.encode(), (bs_ip, bs_port))
                            
                        data, server = sock.recvfrom(BUFFER_SIZE)
                        bs_message = data.decode()
                        
                        sock.close()
                        #Check BS response
                        bs_message_split = bs_message.split()
                        if bs_message_split[0] == "DBR" and bs_message_split[1] == "OK":
                            shutil.rmtree(directory_path)
                            reply = "DDR OK\n"
                        else:
                            reply = "DDR NOK\n"
                else:
                    reply = "ERR\n"
            except IndexError:
                break
        conn.sendall(reply.encode())
     
    #came out of loop
    conn.close()

#Function to initiate TCP Server
def tcp_server_init():
    #Variables
    global CS_IP
    global CS_PORT
    
    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
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
    print('<<<Waiting for TCP Connections>>>')
    
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_tcp_thread ,(conn,))
 
    s.close
    os._exit(0)

#Function to initiate UDP Server    
def udp_server_init():
    #Variables
    global CS_IP
    global CS_PORT
    
    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #Get Host Name
    CS_IP = socket.gethostbyname(socket.gethostname())
    
    #Bind Socket to CS IP and CS PORT
    try:
        s.bind((CS_IP, CS_PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    
    print('<<<Waiting for UDP Connections>>>')
    
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        data, address = s.recvfrom(BUFFER_SIZE)
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_udp_thread ,(s,data,address,))
 
    s.close()
    os._exit(0)
    
#Function to initiate server with the the protocol passed by the parent
def central_server_init(protocol):
    if protocol == 0 :
        tcp_server_init()
    else:
        udp_server_init()

#Function to create processes
def parent():
    for i in range(2):
        try:
            pid = os.fork()
        except OSError:
            sys.stderr.write("Could not create a child process\n")
            continue
                    
        if pid == 0 :
            central_server_init(i)
                        
    for i in range(2):
        os.waitpid(0, 0)

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
                parent()
        else:
            print("Invalid Command!")
    else:
        print("Invalid number of commands!")
else:
    parent()
