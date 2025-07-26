import cv2 as cv
import pickle
import socket
import struct
from picamera2 import Picamera2

picam2=Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size":(640, 480)}))
picam2.start()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.196.58',8000)) #server IP address and port
server_socket.listen(10)


try:
	#accept client connection
	client_socket, client_address = server_socket.accept()
	print(f"[*] Accepted connection from {client_address}")
	
	while True:
		im=picam2.capture_array()
		ret, encoded_img = cv.imencode('.jpg',im)
		#serialized_frame = pickle.dumps(im)
		#msg_sz=struct.pack("L", len(serialized_frame))
		data=encoded_img.tobytes()
		msg_header = len(data)
		header = struct.pack('!I',msg_header)
		
		client_socket.sendall(header + data)	
		cv.imshow("Camera",im)

		if (cv.waitKey(1) & 0xFF==ord('q')):
			break


finally:
    # Cleanup
    client_socket.close()
    server_socket.close()
    picam2.stop()
    cv.destroyAllWindows()
    print("[*] Server shut down")
