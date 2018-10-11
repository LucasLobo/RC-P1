# /mnt/c/Users/Utilizador/Documents/GitHub/RC-P1
import sys
import socket
import os.path
import os
import shutil

from _thread import *
from os import path



USER_FILE = "./BackupServer/user_"
BUFFER_SIZE = 1024

CS_IP = socket.gethostbyname(socket.gethostname())
CS_PORT = 58054

BS_IP = ""
BS_PORT = 59000


def is_valid_login(value):
    if len(value) == 2 and len(value[0]) == 5 and value[0].isdigit() and len(value[1]) == 8 and value[1].isalnum():
        return True
    return False

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
            user = split_server_response[1]
            directory = split_server_response[2]
            new_dir = USER_FILE + user + "/" + directory

            files_by_line = subprocess.check_output(['ls','-l','--full-time', new_dir]).decode().splitlines()[1:]
            reply = ["LFD" + str(len(files_by_line))]

            for line in files_by_line:
                split_line = line.split()

                date = ".".join(split_line[5].split("-")[::-1])
                time = split_line[6].split(".")[0]
                filename = split_line[8]
                size = split_line[4]
                reply.extend([filename, date, time, size])


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


        elif (response_code == "DBR"):
            user = split_server_response[1]
            directory = split_server_response[2]
            rem_dir= USER_FILE + user + "/" + directory

            if os.path.exists(rem_dir):
                shutil.rmtree(rem_dir)
                reply = "DBR OK"
            else:
                reply = "DBR NOK"

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
                    content = data.split(b" ", 3)
                    directory = content[1].decode()
                    mumber_of_files = int(content[2].decode())
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
                            file = open('./' + directory + '/' + current_file_info[0].decode(), 'wb')
                            file.write(data)
                            reply = "UPR OK"

                    else:
                        reply = "UPR NOK"


                elif (response_code == "RSB"):
                    "recebe dir"
                    directory = split_client_response[1]

                    if not os.path.exists(directory):
                        user_response = "Directory does not exit"
                        display_fail_messages("Folder does not exist", "backup dir")

                    else:
                        files_by_line = subprocess.check_output(['ls','-l','--full-time', directory]).decode().splitlines()[1:]

                        reply = ["RBR", str(len(files_by_line))]

                        for line in files_by_line:
                            split_line = line.split()

                            date = ".".join(split_line[5].split("-")[::-1])
                            time = split_line[6].split(".")[0]
                            filename = split_line[8]
                            size = split_line[4]
                            reply.extend([filename, date, time, size])



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


f size_commands > 1 and size_commands < 4:
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
