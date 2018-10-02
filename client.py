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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(auth.encode())
    server_response = s.recv(BUFFER_SIZE).decode()
    user_response = ""
    ok = False

    if server_response == "ERR\n":
        user_response = "Error"

    elif server_response == "AUR NEW\n":
        user_response = "User \"" + user + "\" created"

    elif server_response == "AUR OK\n":
        user_response = "User \"" + user + "\" login"
        ok = True

    elif server_response == "AUR NOK\n":
        user_response = "Wrong password"

    else:
        user_response = "Unknown"

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
    s = connect_to_server()
    s.send((command + "\n").encode())
    data = ""
    buffer = s.recv(BUFFER_SIZE).decode()
    while buffer != "":
        data += buffer
        buffer = s.recv(BUFFER_SIZE).decode()

    if data != "":
        print("received data:", data)
    else:
        print(command + " - no return")

    s.close();


user_input = input()
while True:
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


    elif command == "deluser":
        print("deluser")

    elif command == "backup":
        print("backup")

    elif command == "restore":
        print("restore")

    elif command == "dirlist":
        if len(split_input[1:]) == 0:
            process_command("LSD");
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

    user_input = input()
