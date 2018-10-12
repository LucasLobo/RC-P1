#!/usr/bin/env python3
import sys
import socket
import os
import signal
import subprocess
import shutil
from _thread import *
from os import path


USER_FILE = "./BackupServer/user_"
BUFFER_SIZE = 1024

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58054

BS_IP = socket.gethostbyname(socket.gethostname())
BS_PORT = 59000


def is_valid_login(value):
    if len(value) == 2 and len(value[0]) == 5 and value[0].isdigit() and len(value[1]) == 8 and value[1].isalnum():
        return True
    return False

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


#Function for handling TCP connections. This will be used to create threads
def client_tcp_thread(conn):
    global USER_FILE
    user = ""
    password = ""
    server_request = ""

    data = receive_message_tcp(conn)

    client_response = data.decode()
    split_client_response = client_response.split()
    response_code = split_client_response[0]
    if (response_code == "AUT"):
        user = split_client_response[1]
        password = split_client_response[2]

        user_file = USER_FILE + user + ".txt"
        if not path.exists(user_file):
            server_request = ["AUR", "NOK"]

        else:
            f = open(user_file,"r")
            stored_pass = f.read()
            f.close()
            if stored_pass == password:
                server_request = ["AUR", "OK"]
            else:
                server_request = ["AUR", "NOK"]
    elif (response_code == "ERR"):
        print("Error")
    else:
        server_request = ["ERR"]

    if (server_request):
        send_message_tcp(conn, server_request)

    data = receive_message_tcp(conn)
    client_response = data.split()
    response_code = client_response[0].decode()

    if (response_code == "UPL"):
        content = data.split(b" ", 3)
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

            server_request = ["UPR", "OK"]

        else:
            server_request = ["UPR", "NOK"]
    elif (response_code == "RSB"):
        if (len(client_response) == 2):
            directory = USER_FILE + user + "/" + client_response[1].decode()

            if not os.path.exists(directory):
                server_request = ["RBR", "EOF"]

            else:
                files_by_line = subprocess.check_output(['ls','-l','--full-time', directory]).decode().splitlines()[1:]

                server_request = ["RBR", str(len(files_by_line))]

                for line in files_by_line:
                    split_line = line.split()
                    date = ".".join(split_line[5].split("-")[::-1])
                    time = split_line[6].split(".")[0]
                    filename = split_line[8]
                    size = split_line[4]
                    file = open(directory + "/" + filename, 'rb')
                    file_data = file.read()
                    file.close()
                    server_request.extend([filename, date, time, size])
                    server_request.append(file_data)
        else:
            server_request = ["RBR", "ERR"]

    elif (response_code == "ERR"):
        print("Error")
    else:
        server_request = ["ERR"]

    if (server_request):
        send_message_tcp(conn, server_request)
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
        print('Connected with client at ' + addr + ':' + str(port))

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_tcp_thread ,(conn,))

    s.close()
    os._exit(0)


def process_cs_request(s,data,address,port):
    split_server_response = data.decode().split()
    response_code = split_server_response[0]

    if (response_code == "LSF"):
        user = split_server_response[1]
        directory = split_server_response[2]
        new_dir = USER_FILE + user + "/" + directory

        files_by_line = subprocess.check_output(['ls','-l','--full-time', new_dir]).decode().splitlines()[1:]
        reply = "LFD " + str(len(files_by_line))

        for line in files_by_line:
            split_line = line.split()

            date = ".".join(split_line[5].split("-")[::-1])
            time = split_line[6].split(".")[0]
            filename = split_line[8]
            size = split_line[4]
            reply += " " + filename + " " + date + " " + time + " " + size
        reply += "\n"

    elif (response_code == "LSU"):
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

    elif (response_code == "DLB"):
        user = split_server_response[1]
        directory = split_server_response[2]
        rem_dir = USER_FILE + user + "/" + directory

        if os.path.exists(rem_dir):
            shutil.rmtree(rem_dir)
            reply = "DBR OK\n"

            if not os.listdir(USER_FILE + user):
                shutil.rmtree(USER_FILE + user)
                os.remove(USER_FILE + user + ".txt")
            
        else:
            reply = "DBR NOK\n"
    elif (response_code == "ERR"):
        print("Error")

    else:
        reply = "ERR\n"

    if (reply):
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
        print('Connected with CS at ' + address)

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        process_cs_request(s,data,address,port)

    s.close()
    os._exit(0)


#Function to initiate server with the the protocol passed by the parent
def backup_server_init(protocol):
    if protocol == 0:
        tcp_server_init()
    else:
        udp_server_init()

#Function to register BS in CS
def register_to_cs():
    global BS_IP
    global CS_PORT

    Message = "REG " + BS_IP + " " + str(BS_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send registration
        s.sendto(Message.encode(), (CS_IP, CS_PORT))

        # Wait for response
        data, (address,port) = s.recvfrom(BUFFER_SIZE)
        print('Connected with CS at ' + address)
        response = data.decode()
        split_server_response = response.split()
        response_code = split_server_response[0]

        if (response_code == "RGR"):
            status = split_server_response[1]
            if status == "OK":
                reply = "Sucessfull connection"

            elif status == "NOK":
                reply = "Unsucessfull connection"
                print("Bind failed.")
                sys.exit()
            else:
                reply = "Unsucessfull connection"
                print("Bind failed.")
                sys.exit()
        else:
            reply = ""

        s.close()

    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

#Function to unregister BS from CS
def unregister_from_cs():
    global BS_IP
    global CS_PORT

    if (pid != 0):
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
            backup_server_init(i)

    for i in range(2):
        os.waitpid(0, 0)


if not path.exists('BackupServer'):
    os.makedirs('BackupServer')

size_commands = len(sys.argv)

if size_commands % 2 == 1 and size_commands <= 7:

    number_of_options = (size_commands - 1)//2

    try:
        for index in range(0,number_of_options):
            if sys.argv[2 * index + 1] == "-b":
                BS_PORT = int(sys.argv[2 * index + 2])

            elif sys.argv[2 * index + 1] == "-n":
                CS_IP = sys.argv[2 * index + 2] + ".tecnico.ulisboa.pt"

            elif sys.argv[2 * index + 1] == "-p":
                CS_PORT = int(sys.argv[2 * index + 2])

            else:
                print("Unknown option " + sys.argv[1])
                sys.exit()
    except:
        print("Error reading commands")
        sys.exit()

    parent()

else:
    print("Wrong number of arguments")
