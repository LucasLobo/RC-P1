import socket

TCP_IP = 'tejo.tecnico.ulisboa.pt'
TCP_PORT = 58011
BUFFER_SIZE = 1024

user = ""
password = ""
auth = ""

def login_is_valid(value):
    if len(value) == 2 and len(value[0]) == 5 and value[0].isdigit() and len(value[1]) == 8 and value[1].isalnum():
        return True
    return False

def connect_to_server(disconnect_on_end = False, user_login = False):
    global auth
    global user
    global password
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(auth.encode())
    server_response = s.recv(BUFFER_SIZE).decode()
    user_response = ""
    ok = False

    if server_response == "ERR\n":
        user_response = "Error"
        auth = ""
        user = ""
        password = ""

    elif server_response == "AUR NEW\n":
        user_response = "User \"" + user + "\" created"

    elif server_response == "AUR OK\n":
        user_response = "User \"" + user + "\" login"
        ok = True

    elif server_response == "AUR NOK\n":
        user_response = "Wrong password"
        auth = ""
        user = ""
        password = ""

    else:
        user_response = "Unknown"
        auth = ""
        user = ""
        password = ""

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


def process_command(command):
    global user
    global password
    global auth

    s = connect_to_server()
    s.send((command + "\n").encode())
    server_response = ""
    buffer = s.recv(BUFFER_SIZE).decode()
    while buffer != "":
        server_response += buffer
        buffer = s.recv(BUFFER_SIZE).decode()

    if server_response == "":
        print(command + " - no return")

    else:
        split_input = server_response.split()
        response_code = split_input[0]
        user_response = ""

        # Delete user
        if (response_code == "DLR"):
            status = split_input[1]
            if status == "OK":
                user_response = "User \"" + user + "\" successfully deleted."
                user = ""
                password = ""
                auth = ""

            elif status == "NOK":
                user_response = "Remove all files from cloud before deleting user."
            else:
                user_response = "DLR " + status

        # Backup directory
        elif (response_code == "BKR"):
            user_response = "BKR " + ' '.join(split_input[1:])

        # Restore directory
        elif (response_code == "RSR"):
            user_response = "RSR " + ' '.join(split_input[1:])

        # List directories
        elif (response_code == "LDR"):
            # QUESTION: this code includes validation, should it just be 'user_response = server_response' instead?
            if split_input[1].isdigit():
                number_of_dirs = split_input[1]
                user_response = "Number of directories: " + number_of_dirs + "\n" + ' '.join(split_input[2:eval(number_of_dirs)+2])


        # List files in directory
        elif (response_code == "LFD"):
            user_response = "LFD " + ' '.join(split_input[1:])

        # Delete directory
        elif (response_code == "DDR"):
            status = split_input[1]
            if status == "OK":
                user_response = "Directory\"" + command.split()[1]+ "\" successfully removed."

            elif status == "NOK":
                user_response = "Error removing directory \"" + command.split()[1] + "\"."

            else:
                user_response = "DLR " + status

        elif (response_code == "ERR"):
            user_response = "ERR"

        else:
            user_response = "Unknown"

        print(user_response)

    s.close()




user_input = input()
while True:
    if len(user_input) == 0:
        user_input = input()
        continue

    split_input = user_input.split()
    command = split_input[0]

    if command == "exit":
        break

    elif command == "login":
        if login_is_valid(split_input[1:]):
            user = split_input[1]
            auth = "AUT " + split_input[1] + " " + split_input[2] + "\n"
            connect_to_server(True, True)
        else:
            print("Incorrect input: username should be numeric with length 5 and password should be alphanumeric with length 8")

    elif auth != "":
        if command == "deluser":
            if len(split_input[1:]) == 0:
                process_command("DLU")
            else:
                print("Incorrect input: no arguments expected")

        elif command == "backup":
            print("backup")

        elif command == "restore":
            print("restore")

        elif command == "dirlist":
            if len(split_input[1:]) == 0:
                process_command("LSD")
            else:
                print("Incorrect input: no arguments expected")

        elif command == "filelist":
            print("filelist")

        elif command == "delete":
            print("delete")

        elif command == "logout":
            print("logout")

        else:
            print("Unknown command")
    else:
        print("User not authenticated")

    user_input = input()
