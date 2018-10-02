import socket

TCP_IP = 'tejo.tecnico.ulisboa.pt'
TCP_PORT = 58011
BUFFER_SIZE = 1024

auth = ""

def send_message(message):

    # Connect to server and authenticate
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(auth.encode())
    print("received data:", s.recv(BUFFER_SIZE).decode())


    s.send((message + "\n").encode())
    data = ""
    a = s.recv(BUFFER_SIZE).decode()
    while a != "":
        data += a
        a = s.recv(BUFFER_SIZE).decode()

    if (data != ""):
        print("received data:", data)
    else:
        print(message + " - no return")
    s.close()

auth = "AUT " + "99999 zzzzzzzz" + "\n"
send_message("LSD")

send_message("UPL")
