import cv2 as cv
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import serial

fontScale = 1.5
fontFace = cv.FONT_HERSHEY_PLAIN
fontColor = (0, 255, 0)
fontThickness = 1

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
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FPS,60)

    if cap is None:
        print("Camera is not initialised")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("No frames received")
                break
            
            ObjectDetection(frame)
            
            cv.imshow('Object Detection',frame)
            
            if cv.waitKey(1)==ord('q'):
                break
    
    finally:
        cap.release()
        cv.destroyAllWindows()