from googleapiclient.discovery import build
from dotenv import load_dotenv
from pytubefix import YouTube
import os
import pandas as pd
from collections import defaultdict
load_dotenv()
API_KEY = os.getenv('API_KEY')
PROJ_DIR = "C:/Users/bzhu2/github_projects/volley-stats/"

def get_videos(handle_str):
    # Given a youtube channel handle, get all videos from the channel and add to games.csv if not already present.
    # If there are issues processing the title or description, log the video url, title, and description to skipped_games.csv for manual review.
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
    video_url = url if url.startswith('http') else f'https://{url}'

    videos_dir = os.path.join(PROJ_DIR, "videos") # TODO: make this more robust to different environments
    os.makedirs(videos_dir, exist_ok=True)
    
    
    try:
        yt_file = YouTube(video_url, use_po_token=True)
        streams = getattr(yt_file, 'streams', None) or getattr(yt_file, 'fmt_streams', None)
        
        folder_name = file_name.rsplit('.', 1)[0]
        out_dir = os.path.join(videos_dir, folder_name)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, file_name)

        def res_int(s):
            r = getattr(s, 'resolution', None)
            if not r:
                return 0
            if isinstance(r, str) and r.endswith('p'):
                try:
                    return int(r[:-1])
                except Exception:
                    return 0
            return 0

        # 1) Try to find a progressive MP4 (contains audio) at 1080p
        prog_stream = None
        try:
            if getattr(yt_file, 'streams', None):
                # pytube API
                prog_qs = yt_file.streams.filter(progressive=True, file_extension='mp4')
                prog_stream = max(prog_qs, key=res_int) if prog_qs else None
            else:
                # fmt_streams fallback
                candidates = [s for s in streams if getattr(s, 'type', None) == 'video' and getattr(s, 'audio_codec', None)]
                prog_stream = max(candidates, key=res_int) if candidates else None
        except Exception:
            prog_stream = None

        # If we found a progressive MP4 at or above 1080, download and return
        if prog_stream and res_int(prog_stream) >= 1080:
            out_path = os.path.join(out_dir, file_name)
            prog_stream.download(output_path=out_dir, filename=file_name)
            print(f'Download complete: {out_path}')
            return out_path

        # 2) Otherwise, handle adaptive (separate video and audio) streams: download best <=1080p video and best audio, then merge via ffmpeg
        video_candidates = [s for s in streams if getattr(s, 'type', None) == 'video'] if streams else []
        audio_candidates = [s for s in streams if getattr(s, 'type', None) == 'audio'] if streams else []

        if not video_candidates:
            print('No video streams found for this video.')
            return False

        # choose highest video resolution <=1080
        video_choice = None
        try:
            video_choice = max(filter(lambda s: res_int(s) <= 1080, video_candidates), key=res_int)
        except Exception:
            # fallback: highest available
            video_choice = max(video_candidates, key=res_int)

        if not audio_candidates:
            print('No audio streams found — downloading video-only stream (may not be playable).')
            out_path = os.path.join(out_dir, file_name)
            video_choice.download(output_path=out_dir, filename=file_name)
            return out_path

        # pick best audio by abr if available
        def abr_int(s):
            abr = getattr(s, 'abr', None) or getattr(s, 'bitrate', None) or '0'
            try:
                return int(str(abr).replace('kbps', '').strip())
            except Exception:
                return 0

        audio_choice = max(audio_candidates, key=abr_int)

        # Download temp files
        import uuid, subprocess
        tmp_vid_name = f'.tmp_vid_{uuid.uuid4().hex}'
        tmp_aud_name = f'.tmp_aud_{uuid.uuid4().hex}'
        tmp_vid_path = os.path.join(out_dir, tmp_vid_name)
        tmp_aud_path = os.path.join(out_dir, tmp_aud_name)

        print(f'Downloading video stream ({getattr(video_choice, "resolution", "?")})...')
        video_choice.download(output_path=out_dir, filename=tmp_vid_name)
        print('Downloading audio stream...')
        audio_choice.download(output_path=out_dir, filename=tmp_aud_name)

        output_path = os.path.join(out_dir, file_name)
        print('Done downloading. Now merge streams with ffmpeg...')
        # Merge with ffmpeg: try to copy video and encode audio to AAC; fallback to re-encode video if necessary
        ffmpeg_cmd = ['ffmpeg', '-y', '-i', tmp_vid_path, '-i', tmp_aud_path, '-c:v', 'copy', '-c:a', 'aac', output_path]
        try:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'Merged file created: {output_path}')
        except subprocess.CalledProcessError as e:
            print('ffmpeg copy merge failed, retrying with video re-encode (slower).')
            ffmpeg_cmd2 = ['ffmpeg', '-y', '-i', tmp_vid_path, '-i', tmp_aud_path, '-c:v', 'libx264', '-crf', '18', '-preset', 'fast', '-c:a', 'aac', output_path]
            try:
                subprocess.run(ffmpeg_cmd2, check=True)
                print(f'Merged and re-encoded file created: {output_path}')
            except subprocess.CalledProcessError as e2:
                print('ffmpeg failed to merge streams:', e2)
                # Cleanup temp files
                '''try:
                    os.remove(tmp_vid_path)
                except Exception:
                    pass
                try:
                    os.remove(tmp_aud_path)
                except Exception:
                    pass'''
                return False

        # cleanup temp files
        '''try:
            os.remove(tmp_vid_path)
        except Exception:
            pass
        try:
            os.remove(tmp_aud_path)
        except Exception:
            pass'''

        return output_path
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

# Example usage:
#video_file = 'input_videos/test_full_game_1080p.mp4' 
#output_image_folder = 'images/Colan_Rob_Jordan_Stanley'
#frame_to_capture = 379 # Change this to the desired frame number

#extract_periodic_frame(video_file, output_image_folder,10)
#cwd = os.getcwd()
#download_video('https://www.youtube.com/watch?v=1RrhWKeGDRQ')
#clip_video(os.path.join(cwd, 'input_videos\\Rob_Ros_Liam_Zhu.mp4'),90,330,os.path.join(cwd, 'input_videos\\Rob_Ros_Liam_Zhu_90-330.mp4'))
