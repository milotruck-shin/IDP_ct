import cv2 as cv
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import socket
import sys
# import pickle
import numpy as np
import struct
import threading
from queue import Queue


fontScale = 1.5
fontFace = cv.FONT_HERSHEY_PLAIN
fontColor = (0, 255, 0)
fontThickness = 1

stream_active = threading.Event()
video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_client_socket.connect(('192.168.196.58',8000)) #server IP address and port


command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_socket.connect(('192.168.196.58', 8001))


frame_queue=Queue(maxsize=5)

model = YOLO(r"C:\Users\kohji\Downloads\tomato.pt")  #load the YOLO model


# c_header = struct.calcsize("!I") #returns an int

def switch(a):
    if a is None:
        return 0
    else:
        msg = str(a)
        
        command = msg.encode()
        c_header = struct.pack("!I", len(command)) 
        command_socket.sendall(c_header + command)	
        return 1
        

def ObjectDetection(frame):
    results=model.track(source=frame, exist_ok=True, conf = 0.5, imgsz=640, stream = True)
    class_names = model.names

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            if r.boxes.id is not None:
                id = f"ID: {int(box.id[0])}" 
                class_name = class_names[int(box.cls[0])]
                detection = switch(int(box.cls[0]))
                
        
            else:
                id = "ID: N/A"
                
            conf = float(box.conf[0])  # Confidence score
            #c = box.cls
            label = f"{conf:.2f}"
            

            # Draw bounding box
            #annotator.box_label(b, model.names[int(c)])
            cv.rectangle(frame,pt1=(int(x1), int(y1)), pt2=(int(x2), int(y2)), color=(0, 255, 128), thickness = 3, lineType=cv.LINE_8 )
            cv.putText(frame, label, (int(x1), int(y1)-10), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)
            cv.putText(frame, class_name, (int(x1)+60, int(y1)-10), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)
            
            if detection:
                print("Detected, sent to Pi")
            else:
                print("None detected, none to Pi")
    


def client_t():
    try:
        payload_size = struct.calcsize("!I")
        data = bytearray()
        while True:
            while len(data) < payload_size:  #read first 4 bytes
                
                chunk = video_client_socket.recv(4096)
                if not chunk: 
                    print("no chunks")
                    break
                data.extend(chunk)  #add the received chunks to data bytearray
            
            if len(data) < payload_size: #if no more chunks of 4096 to be received, go here and check if received data is correct size, meaning header is complete or not
                print("incorrect size")
                break
                    
            packet_msg_sz =  data[:payload_size]    #for the first 4 bytes of data, thats the header containing packet size
            msg_sz = struct.unpack("!I", packet_msg_sz)[0]   #unpack the bytestream of the header byte
            data = data[payload_size:]  # Remove header, this the the first bytes of the data to be received
            
            #now data size is not 4 bytes anymore, got space to read until 4 bytes
            while len(data) < msg_sz:
                chunk = video_client_socket.recv(4096)
                if not chunk: 
                    break
                data.extend(chunk)
                
            if len(data) < msg_sz: 
                print("incomplete frame")
                break  # Incomplete frame

            # Decode JPEG frame
            frame = cv.imdecode(np.frombuffer(data[:msg_sz], dtype=np.uint8), cv.IMREAD_COLOR)
            print("Frame received!")
            data = data[msg_sz:]  # Clear buffer for next frame

            if frame is None:
                print("Decoded frame is none, skipping.")
                continue
            
            if frame_queue.full():
                frame_queue.get_nowait()
            frame_queue.put_nowait(frame.copy())
            
    except Exception as e :
        print(f"Client thread error: {str(e)}")
        
    finally:
        print("closing socket")
        video_client_socket.close()


def detection_t():
    try:
        while True:
            try:
                frame = frame_queue.get(timeout=0.3)
                
                ObjectDetection(frame)
                cv.imshow('Object Detection',frame)
                
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
            
            except Queue.Empty:
                continue
            
    except Exception as e:
        print(f"Detection thread error: {type(e).__name__}: {str(e)}")
                
    finally:
        cv.destroyAllWindows()


if __name__ == '__main__':

    client_thread = threading.Thread(target=client_t, daemon=True)
    yolo_thread = threading.Thread(target=detection_t, daemon=True)
    client_thread.start()
    yolo_thread.start()
    client_thread.join()
    yolo_thread.join()
