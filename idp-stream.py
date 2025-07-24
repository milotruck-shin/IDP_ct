import cv2 as cv
import pickle
import socket
import struct
from picamera2 import Picamera2

face_detector = cv.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")

cv.startWindowThread()
picam2=Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size":(640, 480)}))
picam2.start()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.1.100',9999)) #server IP address and port
server_socket.listen(10)

#accept client connection
cliet_socket, client_address = server_socket.accept()
print(f"[*] Accepted connection from {client address})

while True:
	im=picam2.capture_array()
	grey=cv.cvtColor(im,cv.COLOR_RGB2GRAY)
	faces=face_detector.detectMultiScale(grey,1.1,5)
	for (x,y,w,h) in faces:
		cv.rectangle(im,(x,y), (x + w, y + h), (0,255,0))

	serialized_frame = pickle.dumps(im)
	msg_sz=struct.pack("L", len(serialized_frame))
	client_socket.sendall(msg_sz + serialized_frame)	
	cv.imshow("Camera",im)
	if cv.waitKey(1)&0xFF==ord('q'):
		break
