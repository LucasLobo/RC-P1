#!/usr/bin/env python3
import sys
import os
import socket
import random
import shutil

from _thread import *
from os import path

# Global Variables
USER_FILE = "./CentralServer/user_"
BS_FILE = "./CentralServer/BS_LIST.txt"

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58054
BUFFER_SIZE = 1024


def receive_message_tcp(conn):
    data = b''
    buffer = conn.recv(BUFFER_SIZE)
    buffer_split = buffer.split(b"\n")
    while (len(buffer_split) == 1):
        data += buffer
        buffer = conn.recv(BUFFER_SIZE)
        buffer_split = buffer.split(b"\n")

    data += buffer_split[0] + b"\n"
    return data

def send_message_tcp(conn, message_array):
    array_len = len(message_array)
    for index in range(array_len):
        if type(message_array[index]) is str:
            conn.sendall(message_array[index].encode())
        else:
            conn.sendall(message_array[index])
        if index < array_len - 1:
            conn.sendall(" ".encode())
    conn.sendall("\n".encode())

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
            stored_bs_split = stored_bs.split(";")[:-1]


            if bs_word in stored_bs_split:
                print(stored_bs_split)
                stored_bs_split.remove(bs_word)
                new_bs_info = ""
                print(stored_bs_split)

                if len(stored_bs_split) > 0:
                    for i in range(len(stored_bs_split)):
                        new_bs_info += stored_bs_split[i] + ";"

                f = open(BS_FILE,"w")
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
    server_request = ""

    #Receiving from client
    client_response = receive_message_tcp(conn)

    if not client_response:
        server_request = ["ERR"]
        send_message_tcp(conn, server_request)
        conn.close()
        return

    try:
        decoded_client_response = client_response.decode()
        split_client_response = decoded_client_response.split()
        response_code = split_client_response[0]

        if response_code == "AUT" and len(split_client_response) == 3:
            user = split_client_response[1]
            password = split_client_response[2]

            user_file = USER_FILE + user + ".txt"

            if not path.exists(user_file):
                os.makedirs(USER_FILE + user)
                f = open(user_file,"w+")
                f.write(password)
                f.close()
                server_request = ["AUR","NEW"]
                print("New user: " + user)
            else:
                f = open(user_file,"r")
                stored_pass = f.read()
                f.close()
                if stored_pass == password:
                    server_request = ["AUR","OK"]
                else:
                    server_request = ["AUR","NOK"]
                    send_message_tcp(conn, server_request)
                    conn.close()
                    return
        else:
            server_request = ["ERR"]
            send_message_tcp(conn, server_request)
            conn.close()
            return
    except:
        server_request = ["ERR"]
        send_message_tcp(conn, server_request)
        conn.close()
        return

    send_message_tcp(conn, server_request)

    #Receiving from client
    client_response = receive_message_tcp(conn)

    if not client_response:
        server_request = ["ERR"]
        send_message_tcp(conn, server_request)
        conn.close()
        return

    try:
        decoded_client_response = client_response.decode()
        split_client_response = decoded_client_response.split()
        response_code = split_client_response[0]

        if response_code == "LSD" and len(split_client_response) == 1:
            print("User: " + user + "\tCommand: List Directories")
            len_dirs = len(os.listdir(USER_FILE + user))
            if len_dirs != 0:
                list_dirs = os.listdir(USER_FILE + user)
                server_request = ["LDR", str(len_dirs)]
                for i in range(len_dirs):
                    server_request += [list_dirs[i]]
            else:
                server_request = ["LDR", "0"]
        elif response_code == "DLU" and len(split_client_response) == 1:
            print("User: " + user + "\tCommand: Delete User")
            len_dirs = len(os.listdir(USER_FILE + user))
            if len_dirs != 0:
                server_request = ["DLR", "NOK"]
            else:
                os.rmdir(USER_FILE + user)
                os.remove(USER_FILE + user + ".txt")
                print("User " + user + " deleted")
                server_request = ["DLR", "OK"]
        elif response_code == "BCK":
            print("User: " + user + "\tCommand: Backup Directory")

            number_files = int(split_client_response[2])
            if (len(split_client_response) - 3) == (number_files * 4):
                directory_name = split_client_response[1]
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

                    client_response, server = sock.recvfrom(BUFFER_SIZE)
                    bs_message = client_response.decode()

                    sock.close()
                    #Check BS response
                    bs_message_split = bs_message.split()
                    if bs_message_split[0] == "LUR" and bs_message_split[1] == "OK":
                        server_request = ["BKR", bs_ip, str(bs_port), str(number_files)]

                        for i in range(3, len(split_client_response)):
                            server_request += [split_client_response[i]]
                    else:
                        server_request = ["BKR", "EOF"]
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

                    client_response, server = sock.recvfrom(BUFFER_SIZE)
                    bs_message = client_response.decode()

                    sock.close()
                    #Check BS response
                    bs_message_split = bs_message.split()
                    if bs_message_split[0] == "LFD":
                        server_request = ["BKR", bs_ip, str(bs_port), bs_message_split[1]]

                        for i in range(2, len(bs_message_split)):
                            server_request += [bs_message_split[i]]
                    else:
                        server_request = ["BKR", "EOF"]
            else:
                server_request = ["BKR", "ERR"]
        elif response_code == "LSF":
            print("User: " + user + "\tCommand: List Directory Files")

            directory_name = split_client_response[1]
            directory_path = USER_FILE + user + "/" + directory_name
            bs_file_dir = directory_path + "/" + "BS.txt"

            if not path.exists(directory_path):
                server_request = ["LFD", "NOK"]
            else:
                #Open BS file in dir
                udp_message = "LSF " + user + " " + directory_name + "\n"

                f = open(bs_file_dir,"r")
                stored_bs = f.read()
                f.close()

                #Get BS
                bs_split = stored_bs.split(",")
                bs_ip = bs_split[0]
                bs_port = int(bs_split[1])
                # Send and receive BS message
                sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock.sendto(udp_message.encode(), (bs_ip, bs_port))

                client_response, server = sock.recvfrom(BUFFER_SIZE)
                bs_message = client_response.decode()

                sock.close()
                #Check BS response
                bs_message_split = bs_message.split()
                if bs_message_split[0] == "LFD":
                    server_request = ["LFD", bs_ip, str(bs_port), bs_message_split[1]]

                    for i in range(2, len(bs_message_split)):
                        server_request += [bs_message_split[i]]
                else:
                    server_request = ["LFD", "NOK"]
        elif response_code == "RST":
            print("User: " + user + "\tCommand: Restore Directory")

            if len(split_client_response) == 2:
                directory_name = split_client_response[1]
                directory_path = USER_FILE + user + "/" + directory_name
                bs_file_dir = directory_path + "/" + "BS.txt"

                if not path.exists(directory_path):
                    server_request = ["RSR", "EOF"]
                else:
                    #Open BS file in dir
                    f = open(bs_file_dir,"r")
                    stored_bs = f.read()
                    f.close()

                    #Get BS
                    bs_split = stored_bs.split(",")
                    bs_ip = bs_split[0]
                    bs_port = int(bs_split[1])

                    server_request = ["RSR", bs_ip, str(bs_port)]
            else:
                server_request = ["RSR", "ERR"]
        elif response_code == "DEL":
            print("User: " + user + "\tCommand: Delete Directory")

            directory_name = split_client_response[1]
            directory_path = USER_FILE + user + "/" + directory_name
            bs_file_dir = directory_path + "/" + "BS.txt"

            if not path.exists(directory_path):
                server_request = ["DDR", "NOK"]
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

                client_response, server = sock.recvfrom(BUFFER_SIZE)
                bs_message = client_response.decode()

                sock.close()
                #Check BS response
                bs_message_split = bs_message.split()
                if bs_message_split[0] == "DBR" and bs_message_split[1] == "OK":
                    shutil.rmtree(directory_path)
                    server_request = ["DDR", "OK"]
                else:
                    server_request = ["DDR", "NOK"]
        else:
            server_request = ["ERR"]

    except:
        server_request = ["ERR"]

    send_message_tcp(conn, server_request)
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

if size_commands == 1:
    parent()
if size_commands == 3:
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
        print("Wrong number of arguments")
