import cv2 as cv
import pickle
import socket
import struct
from picamera2 import Picamera2

cv.startWindowThread()
picam2=Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size":(640, 480)}))
picam2.start()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.14',8000)) #server IP address and port
server_socket.listen(10)

#accept client connection
client_socket, client_address = server_socket.accept()
print(f"[*] Accepted connection from {client_address}")

while True:
    im=picam2.capture_array()    
    serialized_frame = pickle.dumps(im)
    msg_sz=struct.pack("L", len(serialized_frame))
    client_socket.sendall(msg_sz + serialized_frame)	
    cv.imshow("Camera",im)

    if (cv.waitKey(1) & 0xFF==ord('q')):
        break
