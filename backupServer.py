# /mnt/c/Users/Utilizador/Documents/GitHub/RC-P1
import sys
import socket
import os.path
import os

from _thread import *
from os import path


USER_FILE = "./BackupServer/user_"
CS_IP = socket.gethostbyname(socket.gethostname())
BS_PORT = 59000
CS_PORT = 58054
BUFFER_SIZE = 1024
BS_IP = ""



def client_tcp_thread(server_response):
    global USER_FILE
    server_response = server_response.decode()
    split_server_response = server_response.split()
    response_code = split_server_response[0]

    #if (response_code == "REG"):

    if (response_code == "RGR"):
        status = split_server_response[1]
        if status == "OK":
            server_response = "CS confirms" #fillers

        elif status == "NOK":
            server_response = "CS declines"
        else:
            server_response = "RGR ERR"

    #elif (response_code == "UNR"):

    elif (response_code == "UAR"):
        status = split_server_response[1]
        if status == "OK":
            server_response = "CS confirms" #fillers

        elif status == "NOK":
            server_response = "CS declines"
        else:
            server_response = "UAR ERR"

    elif (response_code == "LSF"):
        "filler"

    #elif (response_code == "LFD"):

    elif (response_code == "LSU"):
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


    #elif (response_code == "LUR"):

    #elif (response_code == "DLB"):

    elif (response_code == "DBR"):
        "filler"

    elif (response_code == "ERR"):
        server_response = "ERR"

    else:
        server_response = "Unknown"

    return server_response


def client_udp_thread(conn, data, addr):
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
                    directory = split_client_response[1]
                    mumber_of_files = split_client_response[2]

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    for file_number in range(0,number_of_files):
                        filename = split_client_response[3 + filenumber * 4 -4]
                        date_time = split_client_response[4 + filenumber * 4 -4]
                        size = split_client_response[5 + filenumber * 4 -4]
                        data = split_client_response[6 + filenumber * 4 -4]

                        file_data = open("./" + directory + "/" + filename, 'rb')
                        file_data.write(data)
                        os.utime("./" + directory + "/" + filename, 'rb', (date_time, date_time))


                elif (response_code == "RSB"):
                    "filler"

                elif (response_code == "ERR"):
                    reply = "ERR\n"
            except IndexError:
                break
        sock.sendto(reply.encode() , addr)

    #conn.close()


def udp_client_init():

    global CS_IP
    global CS_PORT

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
        print('Connected with ' + address)

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(client_udp_thread ,(s,data,address,))

    s.close()
    os._exit(0)




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


'''def udp_server_init():
    #Variables
    global BS_IP

    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Get Host Name
    BS_IP = socket.gethostbyname(socket.gethostname())

    try:
        s.bind((BS_IP, BS_PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    #Start listening on Socket
    s.listen(10)
    print('<<<Waiting for Connections>>>')
    connect_upd_server(CS_IP, CS_PORT)

    s.close() '''


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
