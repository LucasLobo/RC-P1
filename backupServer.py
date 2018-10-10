# /mnt/c/Users/Utilizador/Documents/GitHub/RC-P1
import sys
import socket
import os.path
import os

from _thread import *
from os import path


USER_FILE = "./BackupServer/user_"
BUFFER_SIZE = 1024

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58054

BS_IP = ""
BS_PORT = 59000



def client_udp(s):
    global CS_IP
    global CS_PORT

    global USER_FILE
    reply = ""

    while 1:

        data, (address,port) = s.recvfrom(BUFFER_SIZE)
        print('Connected with ' + address)
        response = data.decode()


        split_server_response = response.split()
        response_code = split_server_response[0]



        if (response_code == "RGR"):
            status = split_server_response[1]
            if status == "OK":
                continue #fillers

            elif status == "NOK":
                continue
            else:
                reply = "RGR ERR"

        #elif (response_code == "UNR"):

        elif (response_code == "UAR"):
            status = split_server_response[1]
            if status == "OK":
                reply = "CS confirms" #fillers

            elif status == "NOK":
                reply = "CS declines"
            else:
                reply = "UAR ERR"

        elif (response_code == "LSF"):
            "filler"

        #elif (response_code == "LFD"):

    elif (response_code == "LUR"):
            user = split_server_response[1]
            password = split_server_response[2]

            user_file = USER_FILE + user + ".txt"
            os.makedirs(USER_FILE + user)

            if not path.exists(user_file):
                f = open(user_file,"w+")
                f.write(password)
            else:
                f = open(user_file,"r")
                stored_pass = f.read()
                if stored_pass == password:
                    reply = "LUR OK\n"
                else:
                    reply = "LUR NOK\n"

        elif (response_code == "DBR"):
            "filler"

        elif (response_code == "ERR"):
            reply = "ERR"

        else:
            reply = "Unknown"

        s.sendto(reply.encode() , (CS_IP,CS_PORT))


def client_tcp_thread(conn):
    global USER_FILE
    user = ""
    password = ""
    reply = ""

    while True:
        data = conn.recv(BUFFER_SIZE)

        if not data:
            break
        else:
            client_response = data.decode()
            split_client_response = client_response.split()
            response_code = split_client_response[0]
            try:
                if (response_code == "AUT"):
                    user = split_client_response[1]
                    password = split_client_response[2]

                    user_file = USER_FILE + user + ".txt"
                    os.makedirs(USER_FILE + user)

                    if not path.exists(user_file):
                        reply = "User does not exist"

                    else:
                        f = open(user_file,"r")
                        stored_pass = f.read()
                        if stored_pass == password:
                            reply = "AUR OK\n"
                        else:
                            reply = "AUR NOK\n"

                elif (response_code == "UPL"):
                    # QUESTION : Perguntar ao Lucas como fazer
                    if len(split_client_response) == 2:
                        status = split_client_response[1].decode()
                        if status == "EOF":
                            user_response = "Directory not found"
                        elif status == "ERR":
                            user_response = "Request not correctly formulated"
                        else:
                            user_response = "Unexpected"
                    elif (len(split_server_response) >= 2) and (split_server_response[1].decode().isdigit()):
                        content = client_response.split(b" ", 3)
                        directory = split_client_response[1]
                        mumber_of_files = split_client_response[2]
                        files = content[3:][0]

                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        for file in range(number_of_files):
                            files = files.split(b" ", 4)
                            current_file_info = files[0:4]
                            current_file_size = int(current_file_info[3].decode())
                            remainder = files[4:][0]
                            data = remainder[0:current_file_size]
                            files = remainder[current_file_size+1:]
                            file = open('./' + directory + '/' + current_file_info[0].decode(), 'wb')
                            file.write(data)

                        user_response = "Successfully restored"
                    else:
                        user_response = "Unexpected"


                elif (response_code == "RSB"):
                    "filler"

                elif (response_code == "ERR"):
                    reply = "ERR\n"
            except IndexError:
                break
        conn.sendall(reply.encode())

    conn.close()


def udp_client_init():

    global CS_IP
    global CS_PORT

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # QUESTION: necessario?
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    BS_IP = socket.gethostbyname(socket.gethostname())
    Message = "REG "+ BS_IP + " " + str(BS_PORT)

    try:
        s.sendto(Message.encode(), (CS_IP, CS_PORT))

        client_udp(s)
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()



    s.close()
    os._exit(0)

    #now keep talking with the client
    # while 1:
    #     #wait to accept a connection - blocking call
    #     data, (address,port) = s.recvfrom(BUFFER_SIZE)
    #     print('Connected with ' + address)
    #     data.decode()
    #
    #     #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    #     start_new_thread(client_udp_thread ,(s,data,address,port))



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




def backup_server_init(protocol):
    if protocol == 0 :
        tcp_server_init()
    else:
        udp_client_init()

#Function to create processes
def parent():
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
