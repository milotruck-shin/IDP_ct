import cv2 as cv
import pickle
import socket
import struct
from picamera2 import Picamera2, Preview
import threading
import serial
import time

picam0=Picamera2(0)
picam1=Picamera2(1)

config={"format": 'RGB888', "size":(640, 480)}
picam0.configure(picam0.create_preview_configuration(main=config))
picam1.configure(picam1.create_preview_configuration(main=config))
# picam0.start_preview(Preview.QTGL, x=100,y=300,width=400,height=300)
# picam1.start_preview(Preview.QTGL, x=500,y=300,width=400,height=300)
picam0.start()
picam1.start()
picam0.start_preview()  # Start the preview (opens a window)
picam1.start_preview()  # Start the preview (opens a window)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.196.58',8000)) #server IP address and port
server_socket.listen(10)

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.bind(('192.168.196.58', 8001))
command_socket.listen(10)

shutdown_event=threading.Event()

esp32 = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate =115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=5)

def receive_t():
    payload_size = struct.calcsize("!I")
    message = bytearray()
    client_send_socket, client_send_address = command_socket.accept()
    print(f"[*] Accepted connection from {client_send_address}")
    try:
        while not shutdown_event.is_set():
            while len(message)<payload_size:
                chunk=client_send_socket.recv(1024)
                if not chunk:
                    break
                message.extend(chunk)
            
            if len(message) < payload_size:
                print("Incomplete size")
                break
            
            packet_sz = message[:payload_size] #first 4 bytes of the message stream is header containing payload length
            recv_packet_sz = struct.unpack("!I", packet_sz)[0]  #unpack byte stream and get the actual value of payload length
            message=message[payload_size:]  #remaining byte is the message
            
            while len(message) < recv_packet_sz:
                chunk = client_send_socket.recv(1024)
                if not chunk: 
                    break
                message.extend(chunk)
                
            if len(message) < recv_packet_sz: 
                print("incomplete frame")
                break  # Incomplete frame
            
            try:
                
                command = message[:recv_packet_sz].decode('utf-8')
                print(f"Received message: {str(command)}")
                message = message[recv_packet_sz:]
                
            except UnicodeDecodeError:
                print("Failed to decode message")
                continue
    
    finally:
        client_send_socket.close()
        command_socket.close()
        
            
def livestream_t():
    try:
        #accept client connection
        client_socket, client_address = server_socket.accept()
        print(f"[*] Accepted connection from {client_address}")
        
        while True:
            try:
                im0=picam0.capture_array()
                im1=picam1.capture_array()
                im=cv.hconcat([im0,im1])
                ret, encoded_img = cv.imencode('.jpg',im)
                #serialized_frame = pickle.dumps(im)
                #msg_sz=struct.pack("L", len(serialized_frame))
                data=encoded_img.tobytes()
                msg_header = len(data)
                header = struct.pack('!I',msg_header)
                
                client_socket.sendall(header + data)	
                # cv.imshow("Camera",im)

                # if (cv.waitKey(1) & 0xFF==ord('q')):
                #     break
            except KeyboardInterrupt:
                break

    finally:
        # Cleanup
        client_socket.close()
        server_socket.close()
        picam0.stop_preview()
        picam1.stop_preview()
        picam0.stop()
        picam1.stop()
        shutdown_event.set()
        # cv.destroyAllWindows()
        print("[*] Server shut down")
        
if __name__ == '__main__':
    command_thread=threading.Thread(target=receive_t, daemon=True)
    livestream_thread=threading.Thread(target=livestream_t, daemon=True)
    command_thread.start()
    livestream_thread.start()
    command_thread.join(timeout=1)
    livestream_thread.join(timeout=1)
