import cv2 as cv
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import serial
import socket
import sys
import pickle
import numpy as np
import struct

fontScale = 1.5
fontFace = cv.FONT_HERSHEY_PLAIN
fontColor = (0, 255, 0)
fontThickness = 1


payload_size = struct.calcsize("L")
data=bytearray()

video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
video_client_socket.connect(('192.168.1.100',9999)) #server IP address and port



def ObjectDetection(frame):
    results=model.track(source=frame, exist_ok=True, conf = 0.5, imgsz=640, stream = True)
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0] 
            
            if r.boxes.id is not None:
                id = f"ID: {int(box.id[0])}"  # Correct way to get tracking ID
            else:
                id = "ID: N/A"
                
            conf = float(box.conf[0])  # Confidence score
            #c = box.cls
            label = f"{conf:.2f}"

            # Draw bounding box
            #annotator.box_label(b, model.names[int(c)])
            cv.rectangle(frame,pt1=(int(x1), int(y1)), pt2=(int(x2), int(y2)), color=(0, 255, 128), thickness = 3, lineType=cv.LINE_8 )
            cv.putText(frame, label, (int(x1), int(y1)-10), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)
            cv.putText(frame, id, (int(x1)+30, int(y1)-10), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)


model = YOLO(r"/home/sunwayrobocon/Documents/robocon25/best.engine")  #load the YOLO model


if __name__ == '__main__':
    while True:
        try:
            while len(data) < payload_size:  #read first 4 bytes
                chunk = video_client_socket.recv(4096)
                if not chunk: 
                    break
                data.extend(chunk)  #add the received chunks to data bytearray
            
            if len(data) < payload_size: #if no more chunks of 4096 to be received, go here and check if received data is correct size, meaning header is complete or not
                break
                    
            packet_msg_sz =  data[:payload_size]    #for the first 4 bytes of data, thats the header containing packet size
            msg_sz = struct.unpack("L", packet_msg_sz)[0]   #unpack the bytestream
            data = data[payload_size:]  # Remove header, this the the first bytes of the data to be received
            
            #now data size is not 4 bytes anymore, got space to read until 4 bytes
            while len(data) < msg_sz:
                chunk = video_client_socket.recv(4096)
                if not chunk: 
                    break
                data.extend(chunk)
                
            if len(data) < msg_sz: break  # Incomplete frame

            # Decode JPEG frame
            frame = cv.imdecode(np.frombuffer(data[:msg_sz], dtype=np.uint8), cv.IMREAD_COLOR)
            data = data[msg_sz:]  # Clear buffer for next frame
            
            ObjectDetection(frame)
            
            cv.imshow('Object Detection',frame)
            
            if cv.waitKey(1)==ord('q'):
                break
        
        finally:
            break

        
        
        
        
