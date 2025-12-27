from googleapiclient.discovery import build
from dotenv import load_dotenv
from pytubefix import YouTube
import os
from moviepy import VideoFileClip
load_dotenv()

api_key = os.getenv('API_KEY')

class Match:
    def __init__(self, player1, player2, player3, player4):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4

    def __str__(self):
        return f'{self.player1} and {self.player2} vs {self.player3} and {self.player4}'


def get_videos():
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.channels().list(
        part='contentDetails',
        forHandle='robwilson6755'
        )

    response = request.execute()

    uploads = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads,
        maxResults=50
        )

    title_description_dict = {}
    player_dict = {}

    while request:
        response = request.execute()

        for item in response.get('items', []):
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            v_idx = video_description.find('v.')
            team1 = video_description[:v_idx-1]
            team2 = video_description[v_idx+3:]
            try:
                player1 = team1.split('/')[0]
                player2 = team1.split('/')[1]
                player3 = team2.split('/')[0]
                player4 = team2.split('/')[1]
                match = Match(player1,player2,player3,player4)
                #print(match)
            except:
                print('ISSUE PROCESSING')
                print(video_title,video_description)
                continue
            if video_title in title_description_dict:
                '''print('ERROR')
                print('OLD: ',video_title, title_description_dict[video_title])
                print('NEW: ', video_title, video_description)
                print(video_title, video_description)'''
                continue
            else:
                title_description_dict[video_title] = video_description
        request = youtube.playlistItems().list_next(request, response)

def download_video(url):
    video_url = url

    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if video_stream:
            print(f'Video found: {yt.title}')
            print(f'Downloading video at {video_stream.resolution} resolution...')

            video_stream.download(filename='test_full_game.mp4')
            print('Download complete!')
        else:
            print('No suitable progressive MP4 stream found.')
    except Exception as e:
        print(f'An error occurred: {e}')

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

download_video('https://www.youtube.com/watch?v=wltzN9fDBo8')
clip_video('test_full_game.mp4',240,300,'test_min4-5.mp4')