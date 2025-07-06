"""
Video assembly module using MoviePy to combine assets into final videos.
Single responsibility: Assemble images, videos, and audio into final video output.
"""
import logging
import os
import srt
import ffmpeg
import whisper
from datetime import timedelta
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
    
    def generate_srt_file(self, text: str, duration: float, output_path: str = None):
        """Generate SRT subtitle file.
        
        Args:
            text: The text to display as subtitles
            duration: Duration of the video in seconds
            output_path: Path to save the SRT file
            
        Returns:
            Path to the generated SRT file
        """
        try:
            # Split text into sentences for better subtitle timing
            sentences = text.split('. ')
            if len(sentences) == 1:
                # If no sentences, split by commas or use the whole text
                sentences = text.split(', ') if ',' in text else [text]
            
            # Calculate timing for each subtitle based on text length (more accurate)
            # Remove empty sentences first
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Calculate duration based on text length (words per minute approach)
            sentence_lengths = [len(sentence.split()) for sentence in sentences]
            total_words = sum(sentence_lengths)
            
            subs = []
            current_time = 0.0
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():  # Only add non-empty sentences
                    # Calculate duration based on word count proportion
                    word_count = len(sentence.split())
                    sentence_duration = (word_count / total_words) * duration
                    
                    start_time = timedelta(seconds=current_time)
                    end_time = timedelta(seconds=current_time + sentence_duration)
                    current_time += sentence_duration
                    
                    # Clean up sentence
                    sentence = sentence.strip()
                    if not sentence.endswith('.') and i < len(sentences) - 1:
                        sentence += '.'
                    
                    subtitle = srt.Subtitle(
                        index=i + 1,
                        start=start_time,
                        end=end_time,
                        content=sentence
                    )
                    subs.append(subtitle)
            
            # Generate SRT content
            srt_content = srt.compose(subs)
            
            # Save to file
            if not output_path:
                output_path = os.path.join(Config.OUTPUT_DIR, "subtitles.srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            logger.info(f"Generated SRT file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate SRT file: {str(e)}")
            return None
    
    def generate_srt_with_whisper(self, audio_path: str, output_path: str = None, language: str = None) -> Optional[str]:
        """Generate SRT file with accurate timing using Whisper speech recognition.
        
        Args:
            audio_path: Path to the audio file
            output_path: Path to save the SRT file
            language: Language code for better recognition (e.g., 'ru', 'en')
            
        Returns:
            Path to the generated SRT file or None if failed
        """
        try:
            logger.info(f"Using Whisper for accurate subtitle timing: {os.path.basename(audio_path)}")
            
            # Load Whisper model (use small model for speed)
            model = whisper.load_model("base")
            
            # Map language codes for Whisper (ru-RU -> ru, en-US -> en)
            whisper_language = None
            if language:
                whisper_language = language.split('-')[0].lower()  # ru-RU -> ru, en-US -> en
                logger.info(f"Using language hint for Whisper: {whisper_language}")
            
            # Transcribe audio with word-level timestamps and language hint
            transcribe_options = {"word_timestamps": True}
            if whisper_language:
                transcribe_options["language"] = whisper_language
            
            result = model.transcribe(audio_path, **transcribe_options)
            
            # Extract segments with timing
            segments = result['segments']
            subs = []
            
            for i, segment in enumerate(segments):
                start_time = timedelta(seconds=segment['start'])
                end_time = timedelta(seconds=segment['end'])
                text = segment['text'].strip()
                
                if text:  # Only add non-empty segments
                    subtitle = srt.Subtitle(
                        index=i + 1,
                        start=start_time,
                        end=end_time,
                        content=text
                    )
                    subs.append(subtitle)
            
            # Generate SRT content
            srt_content = srt.compose(subs)
            
            # Save to file
            if not output_path:
                output_path = os.path.join(Config.OUTPUT_DIR, "whisper_subtitles.srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            logger.info(f"Whisper-generated SRT file: {output_path}")
            logger.info(f"Generated {len(subs)} subtitle segments")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate SRT with Whisper: {str(e)}")
            return None
    
    def burn_subtitles_with_ffmpeg(self, video_path: str, srt_path: str, output_path: str) -> Optional[str]:
        """Burn subtitles into video using FFmpeg for better quality.
        
        Args:
            video_path: Path to input video
            srt_path: Path to SRT subtitle file
            output_path: Path for output video with burned subtitles
            
        Returns:
            Path to output video or None if failed
        """
        try:
            logger.info(f"Burning subtitles using FFmpeg: {os.path.basename(srt_path)}")
            
            # Use FFmpeg to burn subtitles with professional styling
            (
                ffmpeg
                .input(video_path)
                .output(
                    output_path,
                    vf=f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00ffffff,OutlineColour=&H00000000,Outline=1,Shadow=1,Alignment=2'",
                    vcodec='libx264',
                    acodec='copy'  # Copy audio without re-encoding
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"FFmpeg subtitle burning complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"FFmpeg subtitle burning failed: {str(e)}")
            return None

    def add_subtitles(self, video_clip, text: str, enable_subtitles: bool = True, subtitle_style: str = "professional"):
        """Add stylized subtitles to a video clip with improved error handling.
        
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
            
            logger.info(f"Adding subtitles with {subtitle_style} style: '{text[:50]}...'")
            
            # Create subtitle text clip with simplified approach for better compatibility
            try:
                # Simple approach - just use basic TextClip with position
                subtitle_clip = TextClip(
                    text=text,
                    font_size=style_config["font_size"],
                    color=style_config["color"],
                    method='caption',
                    size=(self.resolution[0], None)  # Fixed: Add size parameter for caption method
                )
                
                # Position at bottom with margin
                y_position = video_clip.h - Config.SUBTITLE_MARGIN - style_config["font_size"]
                subtitle_clip = subtitle_clip.with_position(('center', y_position))
                subtitle_clip = subtitle_clip.with_duration(video_clip.duration)
                
                # Create composite video
                final_video = CompositeVideoClip([video_clip, subtitle_clip])
                
                logger.info("Successfully added subtitles with simplified approach")
                return final_video
                
            except Exception as e:
                logger.warning(f"Simplified subtitle approach failed: {e}")
                
                # Ultra-basic fallback
                try:
                    subtitle_clip = TextClip(
                        text=text,
                        font_size=36,
                        color='white'
                    )
                    subtitle_clip = subtitle_clip.with_position(('center', 'bottom'))
                    subtitle_clip = subtitle_clip.with_duration(video_clip.duration)
                    
                    final_video = CompositeVideoClip([video_clip, subtitle_clip])
                    logger.info("Successfully added subtitles with basic fallback")
                    return final_video
                    
                except Exception as e2:
                    logger.error(f"All subtitle approaches failed: {e2}")
                    return video_clip
            
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
                        # Calculate how many loops needed and create looped video
                        loops_needed = int(audio_clip.duration / final_video.duration) + 1
                        repeated_clips = [final_video] * loops_needed
                        extended_video = concatenate_videoclips(repeated_clips, method="chain")
                        # Trim to exact audio duration
                        final_video = extended_video.subclipped(0, audio_clip.duration)
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
            
            # Add subtitles if requested (optional)
            if enable_subtitles and subtitle_text:
                logger.info("Adding subtitles to video")
                
                # Generate SRT file first - try Whisper for accurate timing
                srt_path = output_path.replace('.mp4', '.srt') if output_path else None
                
                # Try Whisper method first (more accurate), fallback to text-based
                # Pass language information to Whisper for better recognition
                voice_language = None
                if audio_path:
                    # Try to detect language from audio file name or path
                    # This could be improved by passing language as parameter
                    pass
                
                whisper_srt = self.generate_srt_with_whisper(audio_path, srt_path, language=voice_language) if audio_path else None
                if not whisper_srt:
                    logger.info("Whisper method failed, using text-based timing")
                    self.generate_srt_file(subtitle_text, final_video.duration, srt_path)
                else:
                    logger.info("Using Whisper-generated subtitles for accurate timing")
                
                # Skip MoviePy subtitle burning to avoid double subtitles
                # We'll use only FFmpeg subtitle burning for better quality
                logger.info("Skipping MoviePy subtitle burning - will use FFmpeg post-processing")
            
            # Generate output path if not provided
            if output_path is None:
                output_path = os.path.join(Config.OUTPUT_DIR, "generated_video.mp4")
            
            # Write final video with proper audio encoding
            temp_output_path = output_path.replace('.mp4', '_temp.mp4') if enable_subtitles and subtitle_text else output_path
            logger.info(f"Writing final video: {temp_output_path}")
            final_video.write_videofile(
                temp_output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Apply FFmpeg subtitle burning if subtitles are enabled
            if enable_subtitles and subtitle_text and temp_output_path != output_path:
                logger.info("Applying FFmpeg subtitle burning...")
                srt_path = output_path.replace('.mp4', '.srt')
                if self.burn_subtitles_with_ffmpeg(temp_output_path, srt_path, output_path):
                    # Clean up temporary file
                    try:
                        os.remove(temp_output_path)
                        logger.info("FFmpeg subtitle burning successful, cleaned up temp file")
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file: {e}")
                else:
                    # FFmpeg failed, rename temp file to final output
                    try:
                        os.rename(temp_output_path, output_path)
                        logger.warning("FFmpeg subtitle burning failed, using video without subtitles")
                    except Exception as e:
                        logger.error(f"Failed to rename temp file: {e}")
            
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
                
                # Also generate SRT file for external use
                srt_path = output_path.replace('.mp4', '.srt') if output_path else None
                self.generate_srt_file(subtitle_text, final_video.duration, srt_path)
            
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