"""
Video assembly module using MoviePy to combine assets into final videos.
Single responsibility: Assemble images, videos, and audio into final video output.
"""
import logging
import os
from typing import List, Optional, Dict, Union

from moviepy import (
    VideoFileClip, ImageClip, AudioFileClip, 
    concatenate_videoclips, CompositeVideoClip, TextClip
)

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAssembler:
    """Handles video assembly using MoviePy."""
    
    def __init__(self, fps: int = None, resolution: tuple = None):
        """Initialize video assembler with settings.
        
        Args:
            fps: Frames per second for output video
            resolution: Video resolution as (width, height)
        """
        self.fps = fps or Config.DEFAULT_FPS
        self.resolution = resolution or Config.DEFAULT_RESOLUTION
        
        # Ensure directories exist
        Config.ensure_directories()
    
    def add_subtitles(self, video_clip, text: str, enable_subtitles: bool = True, subtitle_style: str = "professional"):
        """Add stylized subtitles to a video clip.
        
        Args:
            video_clip: The video clip to add subtitles to
            text: The text to display as subtitles
            enable_subtitles: Whether to enable subtitles
            subtitle_style: Style of subtitles ('professional', 'modern', 'cinematic')
            
        Returns:
            Video clip with subtitles added
        """
        if not enable_subtitles or not text:
            return video_clip
            
        try:
            # Get style configuration
            style_config = Config.SUBTITLE_STYLES.get(subtitle_style, Config.SUBTITLE_STYLES["professional"])
            
            logger.info(f"Adding subtitles with {subtitle_style} style")
            
            # Create subtitle text clip with correct MoviePy 2.1.2 parameters
            try:
                # Use correct MoviePy 2.1.2 API
                subtitle_clip = TextClip(
                    text=text,
                    font_size=style_config["font_size"],
                    color=style_config["color"],
                    stroke_color=style_config["stroke_color"],
                    stroke_width=style_config["stroke_width"],
                    method='caption',
                    size=self.resolution
                )
            except Exception as e:
                logger.warning(f"Failed with advanced styling, using basic: {e}")
                # Fallback to basic subtitle without stroke
                subtitle_clip = TextClip(
                    text=text,
                    font_size=style_config["font_size"],
                    color=style_config["color"],
                    method='caption',
                    size=self.resolution
                )
            
            # Position subtitles with better styling
            subtitle_clip = subtitle_clip.set_position(('center', 'bottom')).set_margin(Config.SUBTITLE_MARGIN)
            subtitle_clip = subtitle_clip.set_duration(video_clip.duration)
            
            # Add shadow effect (simulated with multiple text layers)
            shadow_offset = style_config["shadow_offset"]
            if shadow_offset != (0, 0):
                # Create shadow clip with correct parameters
                shadow_clip = TextClip(
                    text=text,
                    font_size=style_config["font_size"],
                    color='black',  # Shadow color
                    method='caption',
                    size=self.resolution
                )
                
                # Position shadow with offset
                shadow_x = 'center' if shadow_offset[0] == 0 else f'center+{shadow_offset[0]}'
                shadow_y = f'bottom+{shadow_offset[1]}'
                shadow_clip = shadow_clip.set_position((shadow_x, shadow_y)).set_margin(Config.SUBTITLE_MARGIN)
                shadow_clip = shadow_clip.set_duration(video_clip.duration)
                
                # Composite video with shadow and subtitles
                final_video = CompositeVideoClip([video_clip, shadow_clip, subtitle_clip])
            else:
                # Composite video with subtitles only
                final_video = CompositeVideoClip([video_clip, subtitle_clip])
            
            logger.info(f"Successfully added {subtitle_style} subtitles")
            return final_video
            
        except Exception as e:
            logger.warning(f"Failed to add subtitles: {str(e)}")
            return video_clip
    
    def create_video_from_assets(
        self,
        image_paths: List[str] = None,
        video_paths: List[str] = None,
        audio_path: str = None,
        output_path: str = None,
        image_duration: float = None,
        subtitle_text: str = None,
        enable_subtitles: bool = False,
        subtitle_style: str = "professional"
    ) -> Optional[str]:
        """Create video from mixed assets.
        
        Args:
            image_paths: List of image file paths
            video_paths: List of video file paths
            audio_path: Path to audio file
            output_path: Output video path
            image_duration: Duration for each image in seconds
            subtitle_text: Text to display as subtitles
            enable_subtitles: Whether to enable subtitles
            
        Returns:
            Path to output video file, or None if failed
        """
        try:
            clips = []
            image_duration = image_duration or Config.DEFAULT_DURATION
            
            # Process image files
            if image_paths:
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        logger.info(f"Adding image: {os.path.basename(image_path)}")
                        img_clip = ImageClip(image_path, duration=image_duration)
                        img_clip = img_clip.resized(self.resolution)
                        clips.append(img_clip)
                    else:
                        logger.warning(f"Image not found: {image_path}")
            
            # Process video files
            if video_paths:
                for video_path in video_paths:
                    if os.path.exists(video_path):
                        logger.info(f"Adding video: {os.path.basename(video_path)}")
                        try:
                            video_clip = VideoFileClip(video_path)
                            video_clip = video_clip.resized(self.resolution)
                            clips.append(video_clip)
                        except Exception as e:
                            logger.error(f"Failed to load video {video_path}: {str(e)}")
                    else:
                        logger.warning(f"Video not found: {video_path}")
            
            if not clips:
                logger.error("No valid clips found to assemble")
                return None
            
            # Concatenate all clips
            logger.info(f"Concatenating {len(clips)} clips")
            final_video = concatenate_videoclips(clips, method="chain")
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Adding audio: {os.path.basename(audio_path)}")
                try:
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Strategy: Always make the video match the audio duration for better experience
                    logger.info(f"Video duration: {final_video.duration}s, Audio duration: {audio_clip.duration}s")
                    
                    if audio_clip.duration > final_video.duration:
                        logger.info(f"Extending video from {final_video.duration}s to {audio_clip.duration}s")
                        # Loop video to match audio duration
                        final_video = final_video.loop(duration=audio_clip.duration)
                    elif audio_clip.duration < final_video.duration:
                        logger.info(f"Trimming video from {final_video.duration}s to {audio_clip.duration}s")
                        # Trim video to match audio duration (preserves all audio)
                        final_video = final_video.subclipped(0, audio_clip.duration)
                    else:
                        logger.info("Video and audio durations match perfectly")
                    
                    # Set audio - now durations should match
                    # Try different audio methods for MoviePy compatibility
                    try:
                        final_video = final_video.with_audio(audio_clip)
                        logger.info("Audio successfully integrated into video (with_audio)")
                    except AttributeError:
                        try:
                            final_video = final_video.set_audio(audio_clip)
                            logger.info("Audio successfully integrated into video (set_audio)")
                        except AttributeError:
                            # Manual audio addition as fallback
                            final_video.audio = audio_clip
                            logger.info("Audio successfully integrated into video (manual)")
                    
                except Exception as e:
                    logger.error(f"Failed to add audio: {str(e)}")
                    # Continue without audio rather than failing
            
            # Add subtitles if requested
            if enable_subtitles and subtitle_text:
                logger.info("Adding subtitles to video")
                final_video = self.add_subtitles(final_video, subtitle_text, enable_subtitles, subtitle_style)
            
            # Generate output path if not provided
            if output_path is None:
                output_path = os.path.join(Config.OUTPUT_DIR, "generated_video.mp4")
            
            # Write final video with proper audio encoding
            logger.info(f"Writing final video: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up clips
            for clip in clips:
                if hasattr(clip, 'close'):
                    clip.close()
            if 'audio_clip' in locals():
                audio_clip.close()
            final_video.close()
            
            logger.info(f"Video assembly complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video assembly failed: {str(e)}")
            return None
    
    def create_slideshow_video(
        self,
        image_paths: List[str],
        audio_path: str = None,
        output_path: str = None,
        image_duration: float = None,
        transition_duration: float = 0.5,
        subtitle_text: str = None,
        enable_subtitles: bool = False,
        subtitle_style: str = "professional"
    ) -> Optional[str]:
        """Create a slideshow video from images.
        
        Args:
            image_paths: List of image file paths
            audio_path: Optional audio file path
            output_path: Output video path
            image_duration: Duration for each image
            transition_duration: Duration of fade transitions
            subtitle_text: Text to display as subtitles
            enable_subtitles: Whether to enable subtitles
            
        Returns:
            Path to output video file, or None if failed
        """
        try:
            if not image_paths:
                logger.error("No images provided for slideshow")
                return None
            
            image_duration = image_duration or Config.DEFAULT_DURATION
            clips = []
            
            for i, image_path in enumerate(image_paths):
                if not os.path.exists(image_path):
                    logger.warning(f"Image not found: {image_path}")
                    continue
                
                logger.info(f"Processing image {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
                
                # Create image clip
                img_clip = ImageClip(image_path, duration=image_duration)
                img_clip = img_clip.resized(self.resolution)
                
                # Add fade transitions
                if i == 0:
                    # First image: fade in
                    img_clip = img_clip.fadein(transition_duration)
                elif i == len(image_paths) - 1:
                    # Last image: fade out
                    img_clip = img_clip.fadeout(transition_duration)
                else:
                    # Middle images: fade in and out
                    img_clip = img_clip.fadein(transition_duration).fadeout(transition_duration)
                
                clips.append(img_clip)
            
            if not clips:
                logger.error("No valid images found for slideshow")
                return None
            
            # Concatenate with smooth transitions
            final_video = concatenate_videoclips(clips, method="chain")
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Adding background audio: {os.path.basename(audio_path)}")
                try:
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Strategy: Always preserve the full audio
                    logger.info(f"Slideshow duration: {final_video.duration}s, Audio duration: {audio_clip.duration}s")
                    
                    if audio_clip.duration > final_video.duration:
                        logger.info("Extending slideshow to match audio duration")
                        final_video = final_video.loop(duration=audio_clip.duration)
                    elif audio_clip.duration < final_video.duration:
                        logger.info("Trimming slideshow to match audio duration")
                        final_video = final_video.subclipped(0, audio_clip.duration)
                    
                    # Set audio with compatibility handling
                    try:
                        final_video = final_video.with_audio(audio_clip)
                        logger.info("Audio successfully integrated into slideshow (with_audio)")
                    except AttributeError:
                        try:
                            final_video = final_video.set_audio(audio_clip)
                            logger.info("Audio successfully integrated into slideshow (set_audio)")
                        except AttributeError:
                            final_video.audio = audio_clip
                            logger.info("Audio successfully integrated into slideshow (manual)")
                    
                except Exception as e:
                    logger.error(f"Failed to add audio: {str(e)}")
            
            # Add subtitles if requested
            if enable_subtitles and subtitle_text:
                logger.info("Adding subtitles to slideshow")
                final_video = self.add_subtitles(final_video, subtitle_text, enable_subtitles, subtitle_style)
            
            # Generate output path if not provided
            if output_path is None:
                output_path = os.path.join(Config.OUTPUT_DIR, "slideshow_video.mp4")
            
            # Write final video
            logger.info(f"Writing slideshow video: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            for clip in clips:
                if hasattr(clip, 'close'):
                    clip.close()
            if 'audio_clip' in locals():
                audio_clip.close()
            final_video.close()
            
            logger.info(f"Slideshow video complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Slideshow creation failed: {str(e)}")
            return None
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get information about a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "filename": os.path.basename(video_path)
            }
            clip.close()
            return info
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {}


def create_video_from_files(
    image_files: List[str] = None,
    video_files: List[str] = None,
    audio_file: str = None,
    output_file: str = None
) -> Optional[str]:
    """Utility function to quickly create video from files.
    
    Args:
        image_files: List of image file paths
        video_files: List of video file paths
        audio_file: Audio file path
        output_file: Output video path
        
    Returns:
        Path to created video file
    """
    assembler = VideoAssembler()
    return assembler.create_video_from_assets(
        image_paths=image_files,
        video_paths=video_files,
        audio_path=audio_file,
        output_path=output_file
    )


if __name__ == "__main__":
    # Example usage
    try:
        # Test with sample files (if they exist)
        sample_images = [
            os.path.join(Config.IMAGES_DIR, f) 
            for f in os.listdir(Config.IMAGES_DIR) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ][:3]  # Max 3 images
        
        sample_videos = [
            os.path.join(Config.CLIPS_DIR, f) 
            for f in os.listdir(Config.CLIPS_DIR) 
            if f.lower().endswith(('.mp4', '.avi', '.mov'))
        ][:2]  # Max 2 videos
        
        sample_audio = None
        audio_files = [
            os.path.join(Config.AUDIO_DIR, f) 
            for f in os.listdir(Config.AUDIO_DIR) 
            if f.lower().endswith(('.mp3', '.wav', '.m4a'))
        ]
        if audio_files:
            sample_audio = audio_files[0]
        
        if sample_images or sample_videos:
            output_path = create_video_from_files(
                image_files=sample_images,
                video_files=sample_videos,
                audio_file=sample_audio
            )
            
            if output_path:
                print(f"Created video: {output_path}")
            else:
                print("Failed to create video")
        else:
            print("No sample assets found. Run asset fetcher first.")
            
    except Exception as e:
        print(f"Error: {e}") 