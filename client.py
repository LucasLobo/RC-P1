#!/usr/bin/env python3
import socket
import sys
import subprocess

TCP_IP = 'tejo.tecnico.ulisboa.pt'
TCP_PORT = 58011
BUFFER_SIZE = 1024

username = ""
password = ""

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

def login_is_valid(value):
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


def connect_to_server(disconnect_on_end = False, user_login = False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except Exception as err:
        sys.exit("OS error: {0}".format(err))

    s.send(("AUT " + username + " " + password + "\n").encode())
    server_response = s.recv(BUFFER_SIZE).decode()
    user_response = ""

    ok = False
    if server_response == "ERR\n":
        user_response = "Error"
        clear_auth()

    elif server_response == "AUR NEW\n":
        user_response = "User \"" + username + "\" created"

    elif server_response == "AUR OK\n":
        user_response = "User \"" + username + "\" login"
        ok = True

    elif server_response == "AUR NOK\n":
        user_response = "Wrong password"
        clear_auth()

    else:
        user_response = "Unknown"
        clear_auth()

    # Check if return message should be printed: On a normal use
    # the OK message should only be printed during login
    if user_login or not ok:
        print(user_response)

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
        elif login_is_valid(user_input[1:]):
            set_auth(user_input[1], user_input[2])
            connect_to_server(True, True)
        else:
            display_fail_messages("Error in arguments", "login user pass", "Username should be numeric with length 5 and password should be alphanumeric with length 8")

    elif user_command == "logout":
        if not is_set_auth():
            print("Error: User already logged out")
            return
        print("Logged out from user \"" + username + "\"")
        clear_auth()
        print("Please login")

    elif user_command == "deluser":
        if len(user_input[1:]) == 0:
            process_client_request("DLU")
        else:
            display_fail_messages("No arguments expected", "deluser")

    elif user_command == "backup":
        if len(user_input[1:]) == 1:
            directory = user_input[1]
            files_by_line = subprocess.check_output(['ls','-l','--full-time', directory]).decode().splitlines()[1:]
            client_request = "BCK " + directory + " " + str(len(files_by_line))
            for line in files_by_line:
                split_line = line.split()

                date = ".".join(split_line[5].split("-")[::-1])
                time = split_line[6].split(".")[0]

                filename = split_line[8]
                date_time = date + " " + time
                size = split_line[4]

                client_request += " " + filename + " " + date_time + " " + size
            process_client_request(client_request)
        else:
            display_fail_messages("Expected one argument", "backup dir", "dir should be the name of the directory you want to backup. Needs to be at the current working path")

    elif user_command == "restore":
        if len(user_input[1:]) == 1:
            process_client_request("RST " + user_input[1])
        else:
            display_fail_messages("Expected one argument", "restore dir", "dir should be the name of the directory you want to restore")

    elif user_command == "dirlist":
        if len(user_input[1:]) == 0:
            process_client_request("LSD")
        else:
            display_fail_messages("No arguments expected", "Usage: dirlist")

    elif user_command == "filelist":
        if len(user_input[1:]) == 1:
            process_client_request("RST " + user_input[1])
        else:
            display_fail_messages("Expected one argument", "filelist dir", "dir should be the name of the directory whose files you want to see")

    elif user_command == "delete":
        if len(user_input[1:]) == 1:
            process_client_request("DEL " + user_input[1])
        else:
            display_fail_messages("Expected one argument", "delete dir", "dir should be the name of the directory you want to delete")

    else:
        print("Unknown command")


def process_client_request(client_request):

    # WARNING: this should be done before processing the command, to avoid processing it and then being denied
    if not is_set_auth():
        print("User not authenticated")
        return

    s = connect_to_server()
    s.send((client_request + "\n").encode())
    server_response = ""
    buffer = s.recv(BUFFER_SIZE).decode()
    while buffer != "":
        server_response += buffer
        buffer = s.recv(BUFFER_SIZE).decode()

    if server_response == "":
        print(client_request + " - no return")

    else:
        split_input = server_response.split()
        response_code = split_input[0]
        user_response = ""

        # Delete user
        if (response_code == "DLR"):
            status = split_input[1]
            if status == "OK":
                user_response = "User \"" + username + "\" successfully deleted"
                clear_auth()

            elif status == "NOK":
                user_response = "Remove all files from cloud before deleting user"
            else:
                user_response = "DLR " + status

        # Backup directory
        elif (response_code == "BKR"):
            user_response = server_response

        # Restore directory
        elif (response_code == "RSR"):
            user_response = server_response

        # List directories
        elif (response_code == "LDR"):
            if split_input[1].isdigit():
                number_of_dirs = int(split_input[1])
                user_response = "Number of directories: " + str(number_of_dirs)
                if number_of_dirs > 0:
                    user_response += "\n" + ' '.join(split_input[2:number_of_dirs+2])


        # List files in directory
        elif (response_code == "LFD"):
            user_response = server_response

        # Delete directory
        elif (response_code == "DDR"):
            status = split_input[1]
            if status == "OK":
                user_response = "Directory \"" + client_request.split()[1]+ "\" successfully removed"

            elif status == "NOK":
                user_response = "Error removing directory \"" + client_request.split()[1] + "\""

            else:
                user_response = "DLR " + status

        elif (response_code == "ERR"):
            user_response = "ERR"

        else:
            user_response = "Unknown"

        print(user_response)

    s.close()


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


user_input = input("Please login \n>>> ")
while True:
    if len(user_input) == 0:
        user_input = input(">>> ")
        continue

    split_user_input = user_input.split()
    if split_user_input[0] == "exit":
        break

    process_command(split_user_input)

    user_input = input(">>> ")
