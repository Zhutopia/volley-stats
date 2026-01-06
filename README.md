WIP
# volley-stats
## Prerequisites:
pip install:
- ultralytics
- pytubefix
- google-api-python-client
- ...

YouTube API Key

## Getting Started
Run main.py with arguments for execution of different modes

```bash
py main.py -m mode ...
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