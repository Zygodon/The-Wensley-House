
# CONTROL SIXFAB USER LED FROM REMOTE CLIENT
# UV4L WebCRT must be running for this to work.
# Sixfab HAT must be powered up (by setting GPIO 26 low if necessary)
# pigpio needs to be running too: sudo pigpiod
# On WebCRT "Call", a connection to the uv4l socket is established.
# On sending up arrow from the remote client, sixfab HAT User LED switches on
# On sending down arrow, User led switches off
# Any other key terminates execution.

import os
import socket
import time
import pigpio

socket_path = '/tmp/uv4l.socket'

try:
# Python unlink() removes (deletes)the file path. If the path is a directory,
# OSError is raised
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise # Raises an exception - but so what?

s = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)

USER_PIN    = 27

NONE        = 0
UP_ARROW    = 1 # To switch it off
DOWN_ARROW  = 2 # To switch it on

print ('socket_path: %s' % socket_path)
s.bind(socket_path)
s.listen(1)
 
def getch(keyChr):
    k = NONE
    try:
        keyCode = int(keyChr)
    except:
        pass
    else:
        if keyCode == 103: 
            k = UP_ARROW
        elif keyCode == 108:
            k = DOWN_ARROW
    finally:
        return k

def cleanup():
    pi.stop()

more = True
while more:
    print ('awaiting connection...')
    connection, client_address = s.accept()
    print ('client_address %s' % client_address)
    try:
        print ('established connection with', client_address)

        pi = pigpio.pi()
        pi.set_mode(27, pigpio.OUTPUT) # GPIO 27 as output: Sixfab user LED

        while True:
            data = connection.recv(16)
            print ('received message"%s"' % data)

            time.sleep(0.01)
            key = getch(data[13:16])

            if key == UP_ARROW:
                pi.write(USER_PIN,1)
            elif key == DOWN_ARROW:
                pi.write(USER_PIN,0)

            if key != NONE:  # up arrow or down arrow
                print ('echo data to client')
                connection.sendall(data)
            else:
                print ('no more data from', client_address)
                more = False
                break
 
    finally:
        # Clean up the connection
        cleanup() 