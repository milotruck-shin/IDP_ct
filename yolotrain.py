from ultralytics import YOLO
import torch
print(torch.cuda.get_device_name())

if __name__ == '__main__':

    # model = YOLO("yolov8m.pt")
    # model.info()
    # results = model.train(data=r"C:\Users\kohji\Desktop\AI\ROBOCON\Basketball Hoop\data.yaml", epochs=60, batch=-1,lr0=0.001,device='cpu')
    # results = model.predict(r"C:\Users\kohji\Desktop\Screenshot (164).png")
    
    model = YOLO("yolov8m.pt")
    results = model.train(data=r"C:\ct4\data.yaml", epochs=40, batch=3,lr0=0.001,lrf=0.1, weight_decay=0.005,device=0)
    results = model.val()  # evaluate model performance on the validation set
    results = model.predict(r"C:\ct4\valid\images", save=True)

    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        obb = result.obb  # Oriented boxes object for OBB outputs
        # result.show()  # display to screen
        result.save(filename=r"C:\Users\Ji Shin\Desktop\results")  # save to disk
        torch.cuda.empty_cache()

    
    
