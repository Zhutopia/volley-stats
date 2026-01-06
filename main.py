import argparse
from util import yt_api, yolo_api#, demos
import os

def download_video(youtube_link, file_name):
    if not os.path.exists('videos'):
        os.mkdir('videos')
    if yt_api.download_video(youtube_link, file_name):
        print(f"Video downloaded successfully to videos/{file_name}")
        return
    else:
        print("Failed to download video.")
        return
    
def analyze_video(video_path):
    print(f"Analyzing video at {video_path}...")
    yolo_api.run_yolo_inference(video_path)
    print("Analysis complete.")
    return

def main():
    parser  = argparse.ArgumentParser(prog='Volley-Stat',
                                      description="Convert volleyball matches to statistics")
    #parser.add_argument('-h', '--help', required=False, help="Show help message and exit")
    parser.add_argument('-m', '--mode', required=True, help="Mode to run: download, process, analyze, report")
    parser.add_argument('-l','--link', required=False, help="YouTube link for downloading video")
    parser.add_argument('-w','--work_dir', required=False, help="Working directory for input files")
    parser.add_argument('-o','--output_path', required=False, help="Output path for processed files")
    parser.add_argument('-f','--file_name', required=False, help="File name")
    parser.add_argument('-v','--video_path', required=False, help="Path to video file for analysis")
    args = parser.parse_args()

    # TODO: HELP MESSAGE

    if args.mode == 'download':
        if args.link and args.file_name:
            link = args.link
            file_name = args.file_name if args.file_name.endswith('.mp4') else args.file_name + '.mp4'
            download_video(link, file_name) # TODO: check that output_path is valid
            return
        else:
            #demos.run_download_demo()
            return
    elif args.mode == 'process':
        print("Processing video with YOLO model...")
    elif args.mode == 'analyze':
        if args.video_path:
            analyze_video(args.video_path)
            return
        else:
            #demos.run_analysis_demo()
            return
    elif args.mode == 'report':
        print("Generating report...")
    else:
        print("Invalid mode selected. Please choose from: download, process, analyze, report.")
    print("Program finished.")
    return

if __name__ == "__main__":
    main()