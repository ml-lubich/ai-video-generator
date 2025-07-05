#!/usr/bin/env python3
"""
Audio verification script for AI Video Generator.
Checks if generated videos contain audio streams.
"""

import os
import subprocess
import sys

def check_video_audio(video_path):
    """Check if a video file contains audio streams."""
    try:
        # Use ffprobe to check for audio streams
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_streams', video_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, "Could not analyze video file"
        
        # Check for audio streams
        has_audio = 'codec_type=audio' in result.stdout
        
        if has_audio:
            # Extract audio info
            lines = result.stdout.split('\n')
            audio_info = {}
            in_audio_stream = False
            
            for line in lines:
                if 'codec_type=audio' in line:
                    in_audio_stream = True
                elif line.startswith('[/STREAM]'):
                    in_audio_stream = False
                elif in_audio_stream and '=' in line:
                    key, value = line.split('=', 1)
                    audio_info[key] = value
            
            return True, {
                'codec': audio_info.get('codec_name', 'unknown'),
                'channels': audio_info.get('channels', 'unknown'),
                'sample_rate': audio_info.get('sample_rate', 'unknown'),
                'duration': audio_info.get('duration', 'unknown')
            }
        else:
            return False, "No audio stream found"
            
    except FileNotFoundError:
        return False, "ffprobe not found (install ffmpeg)"
    except Exception as e:
        return False, str(e)

def main():
    """Main function to test all videos in output directory."""
    output_dir = "output"
    
    if not os.path.exists(output_dir):
        print("❌ No output directory found")
        return
    
    video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print("❌ No video files found in output directory")
        return
    
    print("🔊 Audio Verification Report")
    print("=" * 40)
    print()
    
    for video_file in sorted(video_files):
        video_path = os.path.join(output_dir, video_file)
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        
        has_audio, info = check_video_audio(video_path)
        
        print(f"📹 {video_file}")
        print(f"   Size: {file_size:.1f} MB")
        
        if has_audio:
            print(f"   ✅ Audio: {info['codec']} | {info['channels']} channels | {info['sample_rate']} Hz")
            if 'duration' in info:
                print(f"   ⏱️  Duration: {float(info['duration']):.1f}s")
        else:
            print(f"   ❌ Audio: {info}")
        print()
    
    # Summary
    audio_count = sum(1 for vf in video_files if check_video_audio(os.path.join(output_dir, vf))[0])
    print(f"📊 Summary: {audio_count}/{len(video_files)} videos have audio")
    
    if audio_count == len(video_files):
        print("🎉 All videos have audio! System is working correctly.")
    elif audio_count > 0:
        print("⚠️  Some videos have audio. Recent fixes may have resolved issues.")
    else:
        print("❌ No videos have audio. Check audio integration logic.")

if __name__ == "__main__":
    main() 