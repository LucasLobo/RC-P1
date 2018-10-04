#!/usr/bin/env python
import sys
import socket
from thread import *

#Function for handling connections. This will be used to create threads
def clientthread(conn):
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = conn.recv(BUFFER_SIZE)
        print data
        reply = 'OK...' + data
        if not data: 
            break
     
        conn.sendall(reply)
     
    #came out of loop
    conn.close()

def central_server_init():
    #Create Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'
    
    #Bind Socket to TCP IP and TCP PORT
    try:
        s.bind((TCP_IP, CS_PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
     
    print 'Socket bind complete'
    
    #Start listening on Socket
    s.listen(10)
    print 'Socket now listening'
    
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,))
 
    s.close()

TCP_IP = '127.0.0.1'
CS_PORT = 58054
BUFFER_SIZE = 1024

size_commands = len(sys.argv)

if size_commands > 1 and size_commands < 4:
    if size_commands == 3:
        if sys.argv[1] == "-p":
            CS_PORT = int(sys.argv[2])
            central_server_init()
        else:
            print "Invalid Command!"
    else:
        print "Invalid number of commands!"
else:
    central_server_init()
