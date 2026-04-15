import argparse
import pandas as pd
from util import tmp_yt_api_copy, yt_api, yolo_api, video#, demos
import os

def download_videos(games_csv):
    if not os.path.exists(games_csv):
        print(f"{games_csv} not found. Please provide a valid path to the games.csv file.")
    games = pd.read_csv(games_csv)
    for idx, row in games.iterrows():
        if '3.29' in row['title']:
            break
        # TODO: check if video already downloaded before attempting to download again
        if row['downloaded'] == 1:
            continue
        youtube_link = row['link']
        file_name = f"{row['title']}_{row['game_id']}.mp4"
        if yt_api.download_video(youtube_link, file_name):
            folder_name = file_name.rsplit('.', 1)[0] # What if file name extension is some weird .mp4.mp4 or something?
            print(f"Video downloaded successfully to videos/{folder_name}")
            games.loc[idx, 'downloaded'] = 1
            #games.to_csv(games_csv, index=False)
        else:
            print("Failed to download video.")
    games.to_csv(games_csv, index=False)
    return
    
def get_videos(user_handle):
    csv_file = user_handle + '.csv'
    yt_api.get_videos(user_handle)
    #videos.to_csv#TODO: track videos gathered per user
    #if not os.path.exists(csv_file):
    #    with open(csv_file, 'w') as f:
    #        videos = yt_api.get_videos(user_handle)
            
    
def analyze_video(video_path):
    print(f"Analyzing video at {video_path}...")
    yolo_api.run_inference('models/myFirstTraining.pt',video_path)
    print("Analysis complete.")
    return

def main():
    parser  = argparse.ArgumentParser(prog='Volley-Stat',
                                      description="Convert volleyball matches to statistics")
    #parser.add_argument('-h', '--help', required=False, help="Show help message and exit")
    parser.add_argument('-m', '--mode', required=True, help="Mode to run: download, process, analyze, report, gather")
    parser.add_argument('-l','--link', required=False, help="YouTube link for downloading video")
    parser.add_argument('-w','--work_dir', required=False, help="Working directory for input files")
    parser.add_argument('-o','--output_path', required=False, help="Output path for processed files")
    parser.add_argument('-f','--file_name', required=False, help="File name")
    parser.add_argument('-v','--video_path', required=False, help="Path to video file for analysis")
    parser.add_argument('-u','--user', required=False, help="User handle for the channel you want to use videos from")
    args = parser.parse_args()

    # TODO: HELP MESSAGE

    if args.mode == 'download':
        download_videos('games.csv') # TODO: instead of downloading every game in games.csv, download one at a time and process the game. Should have an option to hold onto video or just return stats and annotated game
        return
    elif args.mode == 'process':
        print("Processing video with YOLO model...") # TODO: this is just replaced by analyze right?
    elif args.mode == 'analyze':
        if args.video_path:
            analyze_video(args.video_path)
            return
        else:
            #demos.run_analysis_demo()
            return
    elif args.mode == 'report':
        print("Generating report...")
    elif args.mode == 'gather':
        print(f"Gathering all videos from {args.user}")
        get_videos(args.user)
    else:
        print("Invalid mode selected. Please choose from: download, process, analyze, report.")
    print("Program finished.")
    return

if __name__ == "__main__":
    main()