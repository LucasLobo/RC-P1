#!/usr/bin/env python3
import socket
import sys
import subprocess
import os

TCP_IP = socket.gethostbyname(socket.gethostname())
TCP_PORT = 58054
BUFFER_SIZE = 1024

CENTRAL_SERVER = "CS"
BACKUP_SERVER = "BS"

username = ""
password = ""

def debug(msg):
    print(msg)

# Receives message until it finds \n and returns a bytes variable
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

# Sends whole message array to the server and separates characters by space
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

def clear_auth():
    global username
    global password
    username = ""
    password = ""

def set_auth(a_user, a_pass):
    global username
    global password
    username = a_user
    password = a_pass

def is_set_auth():
    if username != "" and password != "":
        return True
    else:
        return False

def is_valid_login(value):
    if len(value) == 2 and len(value[0]) == 5 and value[0].isdigit() and len(value[1]) == 8 and value[1].isalnum():
        return True
    return False

def display_fail_messages(error = "", usage = "", tip = ""):
    if (error != ""):
        print("Error: " + error)
    if (usage != ""):
        print("Usage: " + usage)
    if (tip != ""):
        print("Tip: " + tip)

def connect_to_server(ip, port, disconnect_on_end = False, user_login = False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((ip, port))
    except Exception as err:
        sys.exit("OS error (connect_to_server): {0}".format(err))


    send_message_tcp(s, ["AUT", username, password])
    server_response = receive_message_tcp(s).decode()
    console_response = ""

    ok = False
    if server_response == "ERR\n":
        console_response = "Error"
        clear_auth()

    elif server_response == "AUR NEW\n":
        console_response = "User \"" + username + "\" created"

    elif server_response == "AUR OK\n":
        console_response = "User \"" + username + "\" login"
        ok = True

    elif server_response == "AUR NOK\n":
        console_response = "Wrong password"
        clear_auth()

    else:
        console_response = "Unknown"
        clear_auth()

    # Check if return message should be printed: On a normal use
    # the OK message should only be printed during login
    if user_login or not ok:
        print(console_response)

    # Check if the socket should be returned or closed after connecting
    if disconnect_on_end:
        s.close()
        return
    else:
        return s

def process_command(user_input):
    user_command = user_input[0]

    if user_command == "login":
        if is_set_auth():
            print("Error: User \"" + username + "\" already logged in")
            return
        elif is_valid_login(user_input[1:]):
            set_auth(user_input[1], user_input[2])
            connect_to_server(TCP_IP, TCP_PORT, True, True)
        else:
            display_fail_messages("Error in arguments", "login user pass", "Username should be numeric with length 5 and password should be alphanumeric with length 8")

    elif user_command == "logout":
        if not is_set_auth():
            print("Error: User already logged out")
            return
        print("Logged out from user \"" + username + "\"")
        clear_auth()
        print("Write \"exit\" to exit")

    elif user_command == "deluser":
        if len(user_input[1:]) == 0:
            process_client_request(["DLU"], CENTRAL_SERVER)
        else:
            display_fail_messages("No arguments expected", "deluser")

    elif user_command == "backup":
        if len(user_input[1:]) == 1:
            directory = user_input[1]
            if not os.path.exists(directory):
                console_response = "Directory does not exit"
                display_fail_messages("Folder does not exist", "backup dir")
            else:

                files_by_line = subprocess.check_output(['ls','-l','--full-time', directory]).decode().splitlines()[1:]
                client_request = ["BCK", directory, str(len(files_by_line))]

                for line in files_by_line:
                    split_line = line.split()

                    date = ".".join(split_line[5].split("-")[::-1])
                    time = split_line[6].split(".")[0]
                    filename = split_line[8]
                    size = split_line[4]
                    client_request.extend([filename, date, time, size])

                process_client_request(client_request, CENTRAL_SERVER)
        else:
            display_fail_messages("Expected one argument", "backup dir", "dir should be the name of the directory you want to backup. Needs to be at the current working path")

    elif user_command == "restore":
        if len(user_input[1:]) == 1:
            process_client_request(["RST", user_input[1]], CENTRAL_SERVER)
        else:
            display_fail_messages("Expected one argument", "restore dir", "dir should be the name of the directory you want to restore")

    elif user_command == "dirlist":
        if len(user_input[1:]) == 0:
            process_client_request(["LSD"], CENTRAL_SERVER)
        else:
            display_fail_messages("No arguments expected", "Usage: dirlist")

    elif user_command == "filelist":
        if len(user_input[1:]) == 1:
            process_client_request(["LSF", user_input[1]], CENTRAL_SERVER)
        else:
            display_fail_messages("Expected one argument", "filelist dir", "dir should be the name of the directory whose files you want to see")

    elif user_command == "delete":
        if len(user_input[1:]) == 1:
            process_client_request(["DEL", user_input[1]], CENTRAL_SERVER)
        else:
            display_fail_messages("Expected one argument", "delete dir", "dir should be the name of the directory you want to delete")

    else:
        print("Unknown command")

def process_client_request(client_request, server_type, ip = None, port = None):

    if not is_set_auth():
        print("User not authenticated")
        return

    if (ip is None):
        ip = TCP_IP
    if (port is None):
        port = TCP_PORT

    if server_type is not CENTRAL_SERVER and server_type is not BACKUP_SERVER:
        print("Server type \"" + server_type + "\" is not valid")
        return

    s = connect_to_server(ip, port)
    send_message_tcp(s, client_request)
    server_response = receive_message_tcp(s)

    if not server_response:
        print("No return - " + server_type + ": " + " ".join(client_request))
    else:
        console_response = ""
        if server_type is CENTRAL_SERVER:
            console_response = request_cs(client_request, server_response)
        elif server_type is BACKUP_SERVER:
            console_response = request_bs(client_request, server_response)
        print(console_response)
    s.close()

def request_cs(client_request, server_response):
    server_response = server_response.decode()
    split_server_response = server_response.split()
    response_code = split_server_response[0]

    # Delete user
    if (response_code == "DLR"):
        status = split_server_response[1]
        if status == "OK":
            console_response = "User \"" + username + "\" successfully deleted"
            clear_auth()

        elif status == "NOK":
            console_response = "Remove all files from cloud before deleting user"
        else:
            console_response = "Unexpected"

    # Backup directory
    elif (response_code == "BKR"):
        if len(split_server_response) == 2:
            if split_server_response[1] == "EOF":
                console_response = "No BS server available. Try again later"

            elif split_server_response[1] == "ERR":
                console_response = "Request not correctly formulated"
            else:
                console_response = "Unexpected"

        # sucess scenario
        elif (len(split_server_response) >= 4) and (split_server_response[2].isdigit()) and (split_server_response[3].isdigit()) and (len(split_server_response) == 4 + 4 * int(split_server_response[3])):
            ip = split_server_response[1]
            port = int(split_server_response[2])

            directory = client_request[1]

            if not os.path.exists(directory):
                console_response = "Directory does not exit"
                return console_response

            number_of_files = int(split_server_response[3])
            client_request_bs = ["UPL", directory, str(number_of_files)]

            for file_number in range(0,number_of_files):
                start_of_file_info = 4 + file_number * 4
                end_of_file_info = 8 + file_number * 4
                file_data = open("./" + directory + "/" + split_server_response[start_of_file_info], 'rb').read()
                file_info = split_server_response[start_of_file_info : end_of_file_info]
                client_request_bs.extend(file_info)
                client_request_bs.append(file_data)

            process_client_request(client_request_bs, BACKUP_SERVER, ip, port)
            console_response = "Backup server: " + ip + ":" + str(port)
        else:
            console_response = "Unexpected"

    # Restore directory
    elif (response_code == "RSR"):
        if len(split_server_response) == 2:
            if split_server_response[1] == "EOK":
                console_response = "No BS server available. Try again later"

            elif split_server_response[1] == "ERR":
                console_response = "Request not correctly formulated"

            else:
                console_response = "Unexpected"
        elif len(split_server_response) == 3:
            ip = split_server_response[1]
            port = int(split_server_response[2])
            client_request_bs = ["RSB", client_request[1]]

            process_client_request(client_request_bs, BACKUP_SERVER, ip, port)
            console_response = "Backup server: " + ip + ":" + str(port)
        else:
            console_response = "Unexpected"

    # List directories
    elif (response_code == "LDR"):
        if split_server_response[1].isdigit():
            number_of_dirs = int(split_server_response[1])
            console_response = "Number of directories: " + str(number_of_dirs)
            if number_of_dirs > 0:
                console_response += "\n" + ' '.join(split_server_response[2:number_of_dirs+2])
        else:
            console_response = "Unexpected"


    # List files in directory
    elif (response_code == "LFD"):
        if len(split_server_response) == 2:
            if split_server_response[1] == "NOK":
                console_response = "Request cannot be answered"
            else:
                console_response = "Unexpected: " + server_response
        elif (len(split_server_response) >= 4) and (split_server_response[2].isdigit()) and (split_server_response[3].isdigit()) and (len(split_server_response) == 4 + 4 * int(split_server_response[3])):
            ip = split_server_response[1]
            port = split_server_response[2]

            number_of_files = int(split_server_response[3])

            console_response = "Number of files: " + str(number_of_files)

            for file_number in range(0,number_of_files):
                start_of_file_info = 4 + file_number * 4
                end_of_file_info = 8 + file_number * 4
                file_info = split_server_response[start_of_file_info : end_of_file_info]
                readable_file_info = "Name: " + file_info[0] + " | Date: " + file_info[1] + " | Time: " + file_info[2] + " | Size: " + file_info[3] + " bytes"
                console_response += "\n" + readable_file_info

        else:
            console_response = "Unexpected"
    # Delete directory
    elif (response_code == "DDR"):
        status = split_server_response[1]
        if status == "OK":
            console_response = "Directory successfully deleted"

        elif status == "NOK":
            console_response = "Error removing directory"

        else:
            console_response = "Unexpected"

    elif (response_code == "ERR"):
        console_response = "ERR"

    else:
        console_response = "Unknown"

    return console_response

def request_bs(client_request, server_response):
    split_server_response = server_response.split()

    response_code = split_server_response[0].decode()
    if (response_code == "UPR"):
        status = split_server_response[1].decode()
        if status == "OK":
            console_response = "Backup completed"

        elif status == "NOK":
            console_response = "Backup failed"
        else:
            console_response = "Unexpected"
    elif (response_code == "RBR"):
        if len(split_server_response) == 2:
            status = split_server_response[1].decode()
            if status == "EOF":
                console_response = "Directory not found"
            elif status == "ERR":
                console_response = "Request not correctly formulated"
            else:
                console_response = "Unexpected"
        elif (len(split_server_response) >= 2) and (split_server_response[1].decode().isdigit()):

            content = server_response.split(b" ", 2)
            number_of_files = int(content[1].decode())
            files = content[2:][0]

            directory = client_request[1]
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

            console_response = "Successfully restored"
        else:
            console_response = "Unexpected"

    else:
        console_response = "Unknown - BS"
    return console_response

arg_number = len(sys.argv)

if arg_number%2 == 1 and arg_number <= 5:
    current_arg = 1

    while current_arg <= 5 and current_arg + 1 <= arg_number:
        if sys.argv[current_arg] == "-n" and sys.argv[current_arg+1].isalpha():
            TCP_IP = sys.argv[current_arg+1] + '.tecnico.ulisboa.pt'

        elif sys.argv[current_arg] == "-p" and sys.argv[current_arg+1].isdigit():
            TCP_PORT = int(sys.argv[current_arg+1])

        else:
            sys.exit("Invalid Command!")

        current_arg += 2
else:
    sys.exit("Invalid Command!")


user_input = input("Please login\nWrite \"exit\" to exit\n>>> ")
while True:
    if len(user_input) == 0:
        user_input = input(">>> ")
        continue

    split_user_input = user_input.split()
    if split_user_input[0] == "exit":
        break

    process_command(split_user_input)

    user_input = input(">>> ")
