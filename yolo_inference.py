from ultralytics import YOLO

#model = YOLO('yolov8m')
model = YOLO('yolo11l.pt')
model.classes = [0]  # only detect person class (class 0 in COCO dataset)


results = model.predict('test_276-290_1080p.mp4',classes=[0,32], save=True)
print(type(results))#[0])
print('==========================')
for box in results[0].boxes:
    print(box)