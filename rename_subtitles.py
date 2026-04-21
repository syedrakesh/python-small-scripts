import os

# Set the paths for the video and subtitle folders
video_folder = r"/home/rakesh/Desktop/ONE.PIECE.S01.Ep[1-8].1080p.AAC.h265.Multi[Hindi-English-Japanese].COMPLETED"
subtitle_folder = r"/home/rakesh/Desktop/ONE.PIECE.S01.Ep[1-8].1080p.AAC.h265.Multi[Hindi-English-Japanese].COMPLETED/Subs"

# Function to rename subtitles based on the video file name
def rename_subtitles():
    # Get the list of video files in the video folder (sorted by name)
    video_files = sorted([f for f in os.listdir(video_folder) if f.endswith(".mkv")])
    
    # Get the list of subtitle files in the subtitle folder (sorted by name)
    subtitle_files = sorted([f for f in os.listdir(subtitle_folder) if f.endswith(".srt")])
    
    # Ensure there are as many subtitles as there are videos
    if len(video_files) != len(subtitle_files):
        print("The number of video files and subtitle files do not match.")
        return
    
    # Loop through both video and subtitle files
    for video_file, subtitle_file in zip(video_files, subtitle_files):
        # Extract the base name (without extension) from the video file
        video_name = os.path.splitext(video_file)[0]
        
        # Define the new subtitle file name (matching the video file name)
        new_subtitle_file = os.path.join(subtitle_folder, f"{video_name}.srt")
        
        # Get the current subtitle file path
        current_subtitle_file = os.path.join(subtitle_folder, subtitle_file)
        
        # Rename the subtitle file
        os.rename(current_subtitle_file, new_subtitle_file)
        print(f"Renamed subtitle: {current_subtitle_file} -> {new_subtitle_file}")

if __name__ == "__main__":
    rename_subtitles()
