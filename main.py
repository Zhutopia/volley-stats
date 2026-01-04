import argparse
from ultralytics import YOLO
from util import yt_api, yolo_api

model = YOLO("models/myFirstTraining.pt")

results = model.predict("input_videos/test_full_game_1080p.mp4", save=True)
print(results)
print('===========================')
for box in results[0].boxes:
    print(box)

def main():
    parser  = argparse.ArgumentParser(prog='Volley-Stat',
                                      description="Convert volleyball matches to statistics")
    parser.add_argument('-m', '--mode', required=True, help="Mode to run: download, process, analyze")
    parser.add_argument('-l','--link', required=False, help="YouTube link for downloading video")
    parser.add_argument('-w','--work_dir', required=False, help="Working directory for input/output files")
    parser.add_argument('-o','--output_dir', required=False, help="Output directory for processed files")
    args = parser.parse_args()

    if args.mode == 'download':
        print("Downloading video from YouTube...")


if __name__ == "__main__":
    main()