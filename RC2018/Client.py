#!/usr/bin/env python
import sys
import socket

def send_single_message(message):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    
    s.send(message)
    data = s.recv(BUFFER_SIZE)
    
    s.close()

    return data

def send_double_message(message1,message2):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    s.send(message1)
    data = s.recv(BUFFER_SIZE)
    
    data = ""

    s.send(message2)

    a = s.recv(BUFFER_SIZE)
    
    while a != "":
        data = data + a
        a = s.recv(BUFFER_SIZE)
    
    s.close()

    return data

def client_init():
    
    while True:
        client_input = raw_input(">>")
        
        client_commands = client_input.split()
        
        if client_commands[0] == "login":
            if len(client_commands) == 3:
                
                #User info
                USER_NAME = client_commands[1]
                USER_PASS = client_commands[2]
                
                #Construct, Send Message and Receive Server Response
                message = "AUT " + client_commands[1] + " " + client_commands[2] + "\n" 
                output = send_single_message(message)
                
                #Translate Server Response
                outputs = output.split()
                if outputs[0] == "AUR":
                    if outputs[1] == "OK":
                        trans_output = "User " + repr(USER_NAME) + " login sucessful"
                        print trans_output
                    elif outputs[1] == "NEW":
                        trans_output = "User " + repr(USER_NAME) + " created"
                        print trans_output
                    else:
                        trans_output = "User " + repr(USER_NAME) + " incorrect password"
                        print trans_output
                else:
                    print "Error!"
            else:
                print "Invalid Number of Commands! Try again"
        elif client_commands[0] == "dirlist":
            
            #Construct, Send Message and Receive Server Response
            message1 = "AUT " + USER_NAME + " " + USER_PASS + "\n"
            message2 = "LSD\n"
            output = send_double_message(message1,message2)
            
            #Translate Server Response
            outputs = output.split()
            if outputs[0] == "LDR":
                number_dir = int(outputs[1])
                trans_output = ""
                for i in range(number_dir):
                    trans_output = trans_output + outputs[i+2] + " "
                print trans_output
            else:
                print "Error!"
        elif client_commands[0] == "filelist":
            if len(client_commands) == 2:
                
               #Construct, Send Message and Receive Server Response
                message1 = "AUT " + USER_NAME + " " + USER_PASS + "\n"
                message2 = "LSF " + client_commands[1] + "\n"
                output = send_double_message(message1,message2)
                
                #Translate Server Response
                outputs = output.split()
                if outputs[0] == "LFD":
                    if outputs[1] != "NOK":
                        BS_IP = outputs[1]
                        BS_PORT = int(outputs[2])
                        
                        number_files = int(outputs[3])
                        trans_output = "Files in " + client_commands[1] + " directory:"
                        x = 4
                        for i in range(number_files):
                            trans_output = trans_output + "\n" + outputs[x] + " " + outputs[x+1] + " " + outputs[x+2] + " " + outputs[x+3]
                            x = x + 4
                        print trans_output
                    else:
                        print "Reply cannot be answered!"
                else:
                    print "Error!"
            else:
                print "Invalid Number of Commands! Try again"
        elif client_commands[0] == "logout":
            USER_NAME = ""
            USER_PASS = ""
        elif client_commands[0] == "exit":
            break
        else:
            print "Invalid Command! Try again"
        """elif client_commands[0] == "deluser":
            
        elif client_commands[0] == "backup":
            
        elif client_commands[0] == "restore":
            
        elif client_commands[0] == "delete":
        """

TCP_IP = '127.0.0.1'
TCP_PORT = 58054
BUFFER_SIZE = 1024

BS_IP = ""
BS_PORT = 0

USER_NAME = ""
USER_PASS = ""

size_commands = len(sys.argv)

if size_commands > 1 and size_commands < 6:
    if size_commands == 3 or size_commands == 5:
        x = 1
        while x < size_commands:
            if sys.argv[x] == "-n":
                TCP_IP = sys.argv[x+1] + '.tecnico.ulisboa.pt'
            elif sys.argv[x] == "-p":
                TCP_PORT = int(sys.argv[x+1])
            else:
                print "Invalid Command!"
            x = x + 2
        client_init()
    else:
        print "Invalid number of commands!"
else:
    client_init()
