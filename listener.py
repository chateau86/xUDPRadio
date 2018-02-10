#! python2
#Simple listener script for sender development.
import socket
import time
listen_port = 13337
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', listen_port))
sock.setblocking(0)
while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print "{:}: {:}".format(addr, data)
    except socket.error as e:
        #print "{:}".format(e)
        time.sleep(0.1)
        pass