WIP
# volley-stats
## Prerequisites:
pip install:
- ultralytics
- pytubefix
- google-api-python-client
- python-dotenv
- opencv-python
- pandas
- ...

Set up .env file with YouTube API key:
Create a .env file in the same directory as main.py. Create YouTube API Key (link?) through the Google Cloud Console. Copy key from APIs and Services -> Credentials paste it into this line to add to the .env file: YOUTUBE_API_KEY="<paste-key-here>"

How to setup youtube token?
gcloud auth?

Need a YouTube API Key and .env file setup

## Getting Started
Run main.py with arguments for execution of different modes

```bash
py main.py...
    -m, --mode        -  Mode to run in: download, process, analyze, report
    -f, --filename    -  File name the downloaded YouTube video will be named as
    -l, --link        -  Link to YouTube video to be downloaded. Videos will be placed into a "videos" directory
    -w, --work_dir    -  Working directory for input files
    -o, --output_path -  Directory to output files
    -v, --video_path  -  Path to video file for analysis
    -h, --help        -  Print help statement and exit
    -d, --details     -  Print details statement for things like model and resources/environments used and exit
```

Currently only able to:
- download video given the -f and -l arguments and save it into the videos directory
- analyze video given the -v argument. results will show up under a runs directory

In runs/detects/test is a test_clip.avi showing 

Future Plans:
- Split player and ball detector
- optimize models for
- look into optimizing resources for performing jobs
- migrate to google colab... AWS equivalent?
- Detect unique players
- Understand events through the course of a match
- Develop metrics from sets of volleyball games
- Investigate player mechanics and personalized stats
