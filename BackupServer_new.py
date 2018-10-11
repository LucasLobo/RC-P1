#!/usr/bin/env python3
import sys
import socket
import os.path
import os
import signal
from _thread import *
from os import path



USER_FILE = "./BackupServer/user_"
BUFFER_SIZE = 1024

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58054

BS_IP = ""
BS_PORT = 59000


def debug(message):
    print(message)

def is_valid_login(value):
    if len(value) == 2 and len(value[0]) == 5 and value[0].isdigit() and len(value[1]) == 8 and value[1].isalnum():
        return True
    return False

#Function for handling TCP connections. This will be used to create threads
def client_tcp_thread(conn):
    global USER_FILE
    user = ""
    password = ""
    reply = ""

    data = conn.recv(BUFFER_SIZE)

    print(data.decode())
    #infinite loop so that function do not terminate and thread do not end.
    # while True:
    #
    #     #Receiving from client
    #     data = conn.recv(BUFFER_SIZE)
    #
    #     if not data:
    #         break
    #     else:
    #         message = data.decode()
    #         msg_split = message.split()
    #
    #         try:
    #             if msg_split[0] == "AUT" and len(msg_split) == 3:
    #                 user = msg_split[1]
    #                 password = msg_split[2]
    #
    #                 user_file = USER_FILE + user + ".txt"
    #
    #                 if not path.exists(user_file):
    #                     os.makedirs(USER_FILE + user)
    #                     f = open(user_file,"w+")
    #                     f.write(password)
    #                     f.close()
    #                     reply = "AUR NEW\n"
    #                     print("New user: " + user)
    #                 else:
    #                     f = open(user_file,"r")
    #                     stored_pass = f.read()
    #                     f.close()
    #                     if stored_pass == password:
    #                         reply = "AUR OK\n"
    #                     else:
    #                         reply = "AUR NOK\n"
    #             elif msg_split[0] == "LSD" and len(msg_split) == 1:
    #                 print("User: " + user + "\tCommand: List Directories")
    #                 len_dirs = len(os.listdir(USER_FILE + user))
    #                 if len_dirs != 0:
    #                     list_dirs = os.listdir(USER_FILE + user)
    #                     reply = "LDR " + str(len_dirs)
    #                     for i in range(len_dirs):
    #                         reply += " " + list_dirs[i]
    #                     reply += "\n"
    #                 else:
    #                     reply = "LDR 0\n"
    #             elif msg_split[0] == "DLU" and len(msg_split) == 1:
    #                 print("User: " + user + "\tCommand: Delete User")
    #                 len_dirs = len(os.listdir(USER_FILE + user))
    #                 if len_dirs != 0:
    #                     reply = "DLR NOK\n"
    #                 else:
    #                     os.rmdir(USER_FILE + user)
    #                     os.remove(USER_FILE + user + ".txt")
    #                     print("User " + user + " deleted")
    #                     reply = "DLR OK\n"
    #             elif msg_split[0] == "BCK":
    #                 print("User: " + user + "\tCommand: Backup Directory")
    #                 number_files = int(msg_split[2])
    #                 if (len(msg_split) - 3) == (number_files * 4):
    #                     directory_name = msg_split[1]
    #                     directory_path = USER_FILE + user + "/" + directory_name
    #                     bs_file_dir = directory_path + "/" + "BS.txt"
    #                     if not path.exists(directory_path):
    #                         os.makedirs(directory_path)
    #
    #                         #Open BS Database file
    #                         f = open(BS_FILE,"r")
    #                         stored_bs = f.read()
    #                         f.close()
    #
    #                         #Get One BS
    #                         bs_list = stored_bs.split(";")
    #                         chosen_bs = bs_list[random.randint(0,len(bs_list)-2)]
    #                         bs_split = chose_bs.split(",")
    #                         bs_ip = bs_split[0]
    #                         bs_port = int(bs_split[1])
    #
    #                         #Create BS file in dir
    #                         f = open(bs_file_dir,"w+")
    #                         f.write(chosen_bs)
    #                         f.close()
    #
    #                         udp_message = "LSU " + user + " " + password + "\n"
    #
    #                         # Send and receive BS message
    #                         sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #                         sock.sendto(udp_message.encode(), (bs_ip, bs_port))
    #
    #                         data, server = sock.recvfrom(BUFFER_SIZE)
    #                         bs_message = data.decode()
    #
    #                         #Check BS response
    #                         bs_message_split = bs_message.split()
    #                         if bs_message_split[0] == "LUR" and bs_message_split[1] == "OK":
    #                             reply = "BKR " + bs_ip + " " + str(bs_port) + " " + str(number_files)
    #                             i = 3
    #                             for i in range(len(msg_split)):
    #                                 reply += " " + msg_split[i]
    #                             reply += "\n"
    #                         else:
    #                             reply = "BKR EOF\n"
    #                     else:
    #                         #Open BS file in dir
    #                         f = open(bs_file_dir,"r")
    #                         stored_bs = f.read()
    #                         f.close()
    #
    #                         #Get BS
    #                         bs_split = stored_bs.split(",")
    #                         bs_ip = bs_split[0]
    #                         bs_port = int(bs_split[1])
    #
    #                         udp_message = "LSF " + user + " " + directory_name + "\n"
    #
    #                         # Send and receive BS message
    #                         sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #                         sock.sendto(udp_message.encode(), (bs_ip, bs_port))
    #
    #                         data, server = sock.recvfrom(BUFFER_SIZE)
    #                         bs_message = data.decode()
    #
    #                         #Check BS response
    #                         bs_message_split = bs_message.split()
    #                         if bs_message_split[0] == "LFD":
    #                             reply = "BKR " + bs_ip + " " + str(bs_port) + " " + bs_message_split[1]
    #                             i = 2
    #                             for i in range(len(bs_message_split)):
    #                                 reply += " " + msg_split[i]
    #                             reply += "\n"
    #                         else:
    #                             reply = "BKR EOF\n"
    #                 else:
    #                     reply = "BKR ERR\n"
    #             elif msg_split[0] == "LSF" and len(msg_split) == 2:
    #                 print("User: " + user + "\tCommand: List Directory Files")
    #                 directory_name = msg_split[1]
    #                 directory_path = USER_FILE + user + "/" + directory_name
    #                 bs_file_dir = directory_path + "/" + "BS.txt"
    #
    #                 if not path.exists(directory_path):
    #                     reply = "LFD NOK\n"
    #                 else:
    #                     #Open BS file in dir
    #                     f = open(bs_file_dir,"r")
    #                     stored_bs = f.read()
    #                     f.close()
    #
    #                     #Get BS
    #                     bs_split = stored_bs.split(",")
    #                     bs_ip = bs_split[0]
    #                     bs_port = int(bs_split[1])
    #
    #                     udp_message = "LSF " + user + " " + directory_name + "\n"
    #
    #                     # Send and receive BS message
    #                     sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #                     sock.sendto(udp_message.encode(), (bs_ip, bs_port))
    #
    #                     data, server = sock.recvfrom(BUFFER_SIZE)
    #                     bs_message = data.decode()
    #
    #                     #Check BS response
    #                     bs_message_split = bs_message.split()
    #                     if bs_message_split[0] == "LFD":
    #                         reply = "LFD " + bs_ip + " " + str(bs_port) + " " + bs_message_split[1]
    #                         i = 2
    #                         for i in range(len(bs_message_split)):
    #                             reply += " " + msg_split[i]
    #                         reply += "\n"
    #                     else:
    #                         reply = "LFD NOK\n"
    #             elif msg_split[0] == "RST":
    #                 print("User: " + user + "\tCommand: Restore Directory")
    #                 if len(msg_split) == 2:
    #                     directory_name = msg_split[1]
    #                     directory_path = USER_FILE + user + "/" + directory_name
    #                     bs_file_dir = directory_path + "/" + "BS.txt"
    #
    #                     if not path.exists(directory_path):
    #                         reply = "RSR EOF\n"
    #                     else:
    #                         #Open BS file in dir
    #                         f = open(bs_file_dir,"r")
    #                         stored_bs = f.read()
    #                         f.close()
    #
    #                         #Get BS
    #                         bs_split = stored_bs.split(",")
    #                         bs_ip = bs_split[0]
    #                         bs_port = int(bs_split[1])
    #
    #                         reply = "RSR " + bs_ip + " " + bs_port + "\n"
    #                 else:
    #                     reply = "RSR ERR\n"
    #             elif msg_split[0] == "DEL" and len(msg_split) == 2:
    #                 print("User: " + user + "\tCommand: Delete Directory")
    #                 directory_name = msg_split[1]
    #                 directory_path = USER_FILE + user + "/" + directory_name
    #                 bs_file_dir = directory_path + "/" + "BS.txt"
    #
    #                 if not path.exists(directory_path):
    #                     reply = "DDR NOK\n"
    #                 else:
    #                     #Open BS file in dir
    #                     f = open(bs_file_dir,"r")
    #                     stored_bs = f.read()
    #                     f.close()
    #
    #                     #Get BS
    #                     bs_split = stored_bs.split(",")
    #                     bs_ip = bs_split[0]
    #                     bs_port = int(bs_split[1])
    #
    #                     udp_message = "DLB " + user + " " + directory_name + "\n"
    #
    #                     # Send and receive BS message
    #                     sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #                     sock.sendto(udp_message.encode(), (bs_ip, bs_port))
    #
    #                     data, server = sock.recvfrom(BUFFER_SIZE)
    #                     bs_message = data.decode()
    #
    #                     #Check BS response
    #                     bs_message_split = bs_message.split()
    #                     if bs_message_split[0] == "DBR" and bs_message_split[1] == "OK":
    #                         shutil.rmtree(directory_path)
    #                         reply = "DDR OK\n"
    #                     else:
    #                         reply = "DDR NOK\n"
    #             else:
    #                 reply = "ERR\n"
    #         except IndexError:
    #             break
    #     conn.sendall(reply.encode())

    #came out of loop
    conn.close()

#Function to initiate TCP Server
def tcp_server_init():
    #Variables
    global BS_IP
    global BS_PORT

    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Get Host Name
    BS_IP = socket.gethostbyname(socket.gethostname())

    #Bind Socket to CS IP and CS PORT
    try:
        s.bind((BS_IP, BS_PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    #Start listening on Socket
    s.listen(10)
    print('<<<Waiting for TCP Connections>>>')

    #now keep talking with the client
    while True:

        debug("a espera de cliente")
        #wait to accept a connection - blocking call
        conn, (addr,port) = s.accept()
        print('Connected with ' + addr + ':' + str(port))

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_tcp_thread ,(conn,))

    s.close()
    os._exit(0)


def process_cs_request(s,data,address,port):
    print(data.decode())
    split_server_response = data.decode().split()
    response_code = split_server_response[0]
    if (response_code == "LSU"):
        if (len(split_server_response) >= 3) and is_valid_login(split_server_response[1:]):
            user = split_server_response[1]
            password = split_server_response[2]

            user_file = USER_FILE + user + ".txt"
            os.makedirs(USER_FILE + user)

            if not path.exists(user_file):
                f = open(user_file,"w+")
                f.write(password)
                f.close()
                reply = "LUR OK\n"

            else:
                reply = "LUR NOK\n"
        else:
            reply = "LUR ERR\n"


    s.sendto(reply.encode(), (address, port))
    # LSF user dir
    # LSU user pass
    # DLB user dir
    # ERR

def udp_server_init():
    #Variables
    global BS_IP
    global BS_PORT

    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Get Host Name
    BS_IP = socket.gethostbyname(socket.gethostname())

    #Bind Socket to BS IP and BS PORT
    try:
        s.bind((BS_IP, BS_PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('<<<Waiting for UDP Connections>>>')

    #now keep talking with the client
    while True:
        #wait to accept a connection - blocking call
        data, (address,port) = s.recvfrom(BUFFER_SIZE)
        print('Connected with ' + address)

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        process_cs_request(s,data,address,port)

    s.close()
    os._exit(0)


#Function to initiate server with the the protocol passed by the parent
def central_server_init(protocol):
    if protocol == 0:
        tcp_server_init()
    else:
        udp_server_init()

#Function to register BS in CS
def register_to_cs():
    global BS_IP
    global CS_PORT

    BS_IP = socket.gethostbyname(socket.gethostname())
    Message = "REG " + BS_IP + " " + str(BS_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send registration
        s.sendto(Message.encode(), (CS_IP, CS_PORT))

        # Wait for response
        data, (address,port) = s.recvfrom(BUFFER_SIZE)
        print('Connected with ' + address)
        response = data.decode()
        split_server_response = response.split()
        response_code = split_server_response[0]

        if (response_code == "RGR"):
            status = split_server_response[1]
            if status == "OK":
                reply = "RGR OK"

            elif status == "NOK":
                reply = "RGR NOK"
            else:
                reply = "RGR ERR"
        else:
            reply = ""

        print(reply)
        s.close()

    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

#Function to unregister BS from CS
def unregister_from_cs():
    global BS_IP
    global CS_PORT

    if (pid != 0):
        BS_IP = socket.gethostbyname(socket.gethostname())
        Message = "UNR " + BS_IP + " " + str(BS_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Send registration
            s.sendto(Message.encode(), (CS_IP, CS_PORT))

            # Wait for response
            data, (address,port) = s.recvfrom(BUFFER_SIZE)
            print('\nDisconnected from ' + address)
            response = data.decode()
            split_server_response = response.split()
            response_code = split_server_response[0]

            if (response_code == "UAR"):
                status = split_server_response[1]
                if status == "OK":
                    reply = "UAR OK"

                elif status == "NOK":
                    reply = "UAR NOK"
                else:
                    reply = "UAR ERR"
            else:
                reply = ""

            print(reply)

        except socket.error as msg:
            print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

def signal_handler(sig, frame):
    if sig == signal.SIGINT:
        unregister_from_cs()
        sys.exit()

#Function to create processes
def parent():
    global pid
    signal.signal(signal.SIGINT, signal_handler)
    register_to_cs()

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


if not path.exists('BackupServer'):
    os.makedirs('BackupServer')

size_commands = len(sys.argv)

if size_commands > 1 and size_commands < 4:
    if size_commands == 3:
        if sys.argv[1] == "-b":
            try :
                BS_PORT = int(sys.argv[2])
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
