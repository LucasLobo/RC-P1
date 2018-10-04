#!/usr/bin/env python
import sys
import socket

def backup_server_init():
    print "CS_IP: ", CS_IP
    print "CS_PORT: ", CS_PORT
    print "BS_PORT: ", BS_PORT

CS_IP = "127.0.0.1"
BS_PORT = 59000
CS_PORT = 58054
BUFFER_SIZE = 1024

size_commands = len(sys.argv)

if size_commands > 1 and size_commands < 8:
    if size_commands == 3 or size_commands == 5 or size_commands == 7:
        x = 1
        while x < size_commands:
            if sys.argv[x] == "-b":
                BS_PORT = int(sys.argv[x+1])
            elif sys.argv[x] == "-p":
                CS_PORT = int(sys.argv[x+1])
            elif sys.argv[x] == "-n":
                CS_IP = sys.argv[x+1]
            else:
                print "Invalid Command!"
            x = x + 2
        backup_server_init()
    else:
        print "Invalid number of commands!"
else:
    backup_server_init()
