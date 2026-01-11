from googleapiclient.discovery import build
from dotenv import load_dotenv
from pytubefix import YouTube
import os
import cv2
import pandas as pd
from moviepy import VideoFileClip
from datetime import datetime
from collections import defaultdict
load_dotenv()
API_KEY = os.getenv('API_KEY')
PROJ_DIR = "C:/Users/bzhu2/git_projects/volley-stats/"

def get_videos(handle_str):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Get list from the channel object (?)
    request = youtube.channels().list(
        part='contentDetails',
        forHandle=handle_str
        )
    response = request.execute()
    
    # Get uploads from the channel
    uploads = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get video items from playlist
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads,
        maxResults=50
        )

    previous_games = None
    game_counter = 1
    yt_uids = None
    new_entries = defaultdict(list)
    skipped_counter = 0
    skipped_entries = defaultdict(list)

    # if util/games.csv exists, there are previous games that were already gathered
    if os.path.exists('stats/games.csv'):
        previous_games = pd.read_csv('stats/games.csv')
        yt_uids = set(previous_games['yt_uid']) # create a set out of the yt_uids
        
    while request: # While there are more videos to look at from the channel
        response = request.execute() # Get list of video items
        for item in response.get('items', []): # iterate through list of items
            yt_video_id = item['id']
            if previous_games: # If game was previously seen, skip it
                if len(previous_games['yt_uid']) > 0:
                    if yt_video_id in yt_uids:
                        print(f'Already logged {item['snippet']['title']}')
                        continue
            yt_video_url = 'youtube.com/watch?v=' + item['snippet']['resourceId']['videoId']
            game_id = game_counter
            game_counter += 1
            #upload_datetime = datetime.fromisoformat(item['snippet']['publishedAt'])
            game_date_str = item['snippet']['title'].split()[0]
            video_description = item['snippet']['description']
            try:
                game_month, game_day, game_year = game_date_str.split('.')
            except:
                print(f'ISSUE PROCESSING TITLE FOR {item['snippet']['title']}... SKIPPED')
                skipped_entries['yt_video_url'].append(yt_video_url)
                skipped_entries['title'].append(item['snippet']['title'])
                skipped_entries['description'].append(video_description)
                skipped_counter += 1
                continue
            
            v_idx = video_description.find('v.')
            team1 = video_description[:v_idx-1]
            team2 = video_description[v_idx+3:]
            try:
                player1 = team1.split('/')[0]
                player2 = team1.split('/')[1]
                player3 = team2.split('/')[0]
                player4 = team2.split('/')[1]
                new_entries['game_id'].append(game_id)
                new_entries['title'].append(item['snippet']['title'])
                new_entries['description'].append(video_description)
                new_entries['player1'].append(player1)
                new_entries['player2'].append(player2)
                new_entries['player3'].append(player3)
                new_entries['player4'].append(player4)
                new_entries['score'].append('?')
                new_entries['downloaded'].append(0)
                new_entries['link'].append(yt_video_url)  
                new_entries['yt_uid'].append(yt_video_id)
            except:
                print(f'ISSUE PROCESSING DESCRIPTION FOR {item['snippet']['title']}... SKIPPED')
                skipped_entries['yt_video_url'].append(yt_video_url)
                skipped_entries['title'].append(item['snippet']['title'])
                skipped_entries['description'].append(video_description)
                skipped_counter += 1
                continue
        request = youtube.playlistItems().list_next(request, response)
    df = pd.DataFrame(new_entries)
    skipped_df = pd.DataFrame(skipped_entries)
    skipped_df.to_csv('skipped_games.csv', mode='w', index=False, header=True)
    if previous_games:
        df.to_csv('games.csv', mode='a', index=False, header=False)
    else:
        df.to_csv('games.csv', mode='w', index=False, header=True)
    print(f'Added {len(new_entries['game_id'])} new entries to games.csv. Skipped {skipped_counter} videos')

def download_video(url, file_name):
    video_url = url
    
    try:
        yt_file = YouTube(video_url)#, use_po_token=True)
        def get_resolution(s):
            return int(s.resolution[:-1])
        video_stream = max( # TODO: figure out exactly how this works... download as mp4 and highest res
            filter(lambda s: get_resolution(s) <= 1080,
                   filter(lambda s: s.type == 'video', yt_file.fmt_streams)),
                   key=get_resolution
        )
        
        #yt = YouTube(video_url)
        #video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if video_stream:
            #print(f'Video found: {yt.title}')
            #print(f'Downloading video at {video_stream.resolution} resolution...')
            video_stream.download(output_path=os.path.join(PROJ_DIR, "videos"), filename=file_name)
            print('Download complete!')
        else:
            print('No suitable progressive MP4 stream found.')
    except Exception as e:
        print(f'An error occurred: {e}')
    
    return True

def clip_video(input_file, start_time, end_time, output_file):
    try:
        with VideoFileClip(input_file) as video:
            # Get the subclip
            clip = video.subclipped(start_time, end_time)
            # Write the result to a file
            clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"Successfully created clip: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_periodic_frame(video_path, output_folder, interval_seconds=5):
    """
    Extracts a specific frame from a video and saves it as a high-resolution image.

    Args:
        video_path (str): Path to the input video file.
        frame_number (int): The index of the frame to extract (0-based).
        output_path (str): Path to save the output image file (e.g., 'snapshot.png').
    """
    # Open the video file
    vidcap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not vidcap.isOpened():
        print("Error: Could not open video file.")
        return

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval_seconds)

    os.makedirs(output_folder, exist_ok=True)
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = vidcap.read()
        if not ret:
            break

        if frame_count % interval_frames == 0:
            timestamp = int(frame_count / fps)
            filename = os.path.join(output_folder, f'snapshot_{timestamp}s.png')
            cv2.imwrite(filename, frame)
            saved_count += 1
            print(f"Saved snapshot at {timestamp}s to {filename}")
        
        frame_count += 1
    vidcap.release()
    print(f"Done. Extracted {saved_count} snapshots.")

# Example usage:
#video_file = 'input_videos/test_full_game_1080p.mp4' 
#output_image_folder = 'images/Colan_Rob_Jordan_Stanley'
#frame_to_capture = 379 # Change this to the desired frame number

#extract_periodic_frame(video_file, output_image_folder,10)
#cwd = os.getcwd()
#download_video('https://www.youtube.com/watch?v=1RrhWKeGDRQ')
#clip_video(os.path.join(cwd, 'input_videos\\Rob_Ros_Liam_Zhu.mp4'),90,330,os.path.join(cwd, 'input_videos\\Rob_Ros_Liam_Zhu_90-330.mp4'))
