import cv2
from moviepy import VideoFileClip

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