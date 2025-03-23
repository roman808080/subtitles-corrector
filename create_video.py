#!/usr/bin/env python3

import os
import subprocess
import argparse
from pathlib import Path

def create_video_with_subtitles(audio_file, subtitle_file, output_file, duration=None):
    """
    Creates an MP4 video with black background, audio and subtitles.
    
    Args:
        audio_file: Path to the audio file (mp3)
        subtitle_file: Path to the subtitle file (srt)
        output_file: Path for the output video file (mp4)
        duration: Duration of the video in seconds. If None, uses audio file duration.
    """
    # Get audio duration if not provided
    if duration is None:
        try:
            # Get duration using ffprobe
            cmd = [
                'ffprobe', 
                '-v', 'error', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                audio_file
            ]
            duration = float(subprocess.check_output(cmd).decode('utf-8').strip())
            print(f"Detected audio duration: {duration:.2f} seconds")
        except Exception as e:
            print(f"Error detecting audio duration: {e}")
            print("Using default duration of 5 minutes")
            duration = 300  # Default 5 minutes

    # Create a video with black screen and audio
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-f', 'lavfi',  # Use libavfilter virtual input device
        '-i', f'color=c=black:s=1280x720:d={duration}',  # Generate black video
        '-i', audio_file,  # Input audio file
        '-vf', f'subtitles={subtitle_file}',  # Add subtitles
        '-c:v', 'libx264',  # Video codec
        '-c:a', 'aac',  # Audio codec
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        '-shortest',  # End when the shortest input stream ends
        output_file
    ]

    print("Creating video...")
    try:
        subprocess.run(cmd, check=True)
        print(f"Video created successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Create MP4 video with audio and subtitles on black background')
    parser.add_argument('audio_file', help='Path to the audio file (mp3)')
    parser.add_argument('subtitle_file', help='Path to the subtitle file (srt)')
    parser.add_argument('-o', '--output', default='output.mp4', help='Output video file (default: output.mp4)')
    parser.add_argument('-d', '--duration', type=float, help='Video duration in seconds (default: audio length)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        return
    
    if not os.path.exists(args.subtitle_file):
        print(f"Error: Subtitle file not found: {args.subtitle_file}")
        return
    
    # Create video
    create_video_with_subtitles(
        args.audio_file,
        args.subtitle_file,
        args.output,
        args.duration
    )

if __name__ == "__main__":
    main()