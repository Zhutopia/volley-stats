from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
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
