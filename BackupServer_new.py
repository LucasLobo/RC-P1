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

    print("CLIENT TO BS :" + data.decode())

    client_response = data.decode()
    split_client_response = client_response.split()
    response_code = split_client_response[0]
    if (response_code == "AUT"):
        user = split_client_response[1]
        password = split_client_response[2]

        user_file = USER_FILE + user + ".txt"
        if not path.exists(user_file):
            reply = "AUR NOK\n"

        else:
            f = open(user_file,"r")
            stored_pass = f.read()
            f.close()
            if stored_pass == password:
                reply = "AUR OK\n"
            else:
                reply = "AUR NOK\n"

    print(reply)
    conn.sendall(reply.encode())




    new_data = b''

    conn.settimeout(0.5)
    buffer = conn.recv(BUFFER_SIZE)

    while buffer:
        new_data += buffer
        try:
            buffer = conn.recv(BUFFER_SIZE)
        except socket.timeout:
            break


    print("new_data: " + new_data.decode())
    client_response = new_data.decode().split()
    response_code = client_response[0]
    print("response_code: " + response_code)
    if (response_code == "UPL"):
        content = new_data.split(b" ", 3)
        directory = content[1].decode()
        number_of_files = int(content[2].decode())
        files = content[3:][0]


        if os.path.exists(USER_FILE+user):
            new_dir = USER_FILE + user + "/" + directory
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)


            for file in range(number_of_files):
                files = files.split(b" ", 4)
                current_file_info = files[0:4]
                current_file_size = int(current_file_info[3].decode())
                remainder = files[4:][0]
                data = remainder[0:current_file_size]
                files = remainder[current_file_size+1:]
                file = open('./' + new_dir + '/' + current_file_info[0].decode(), 'wb')
                file.write(data)
                file.close()
                reply = "UPR OK"

        else:
            reply = "UPR NOK"
    else:
        reply = "ERR"

    reply += "\n"
    print(reply)
    conn.sendall(reply.encode())
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
