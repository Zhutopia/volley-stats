from ultralytics import YOLO

def run_inference(model_path='models/myFirstTraining.pt', video_path='videos/test_video.mp4')
    model = YOLO(model_path)
    results = model.predict(video_path, save=True)

    print('==========================')
    for box in results[0].boxes:
        print(box)