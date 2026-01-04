from ultralytics import YOLO

model = YOLO('yolov5x6u')
#model = YOLO("models/player_detector.pt")
model.classes = [0]  # only detect person class (class 0 in COCO dataset)

#result = model.track('test_276-290_1080p.mp4', conf=0.65, classes=[0], persist=True, save=True, show=True, stream=False)
results = model.predict('input_videos/test_276-290_1080p.mp4', conf=0.65, save=True)

#results = model.predict('test_276-290_1080p.mp4',classes=[0],conf=0.65 save=True)
print(type(results))#[0])
print('==========================')
for box in results[0].boxes:
    print(box)