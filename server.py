import cv2 as cv
import pickle
import socket
import struct
from picamera2 import Picamera2
import threading

picam2=Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size":(640, 480)}))
picam2.start()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.196.58',8000)) #server IP address and port
server_socket.listen(10)

command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.bind(('192.168.196.58', 8001))
command_socket.listen(10)

def receive_t():
    payload_size = struct.calcsize("!I")
    message = bytearray()
    client_send_socket, client_send_address = command_socket.accept()
    print(f"[*] Accepted connection from {client_send_address}")
    try:
        while True:
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
                command = message.decode('utf-8')
                print(f"Received message: {str(command)}")
                
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
        
if __name__ == '__main__':
    command_thread=threading.Thread(target=receive_t, daemon=True)
    livestream_thread=threading.Thread(target=livestream_t, daemon=True)
    command_thread.start()
    livestream_thread.start()
    command_thread.join()
    livestream_thread.join()
