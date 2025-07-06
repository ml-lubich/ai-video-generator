"""
Pipeline runner orchestrates the complete video generation process.
Single responsibility: Coordinate voice generation, asset fetching, and video assembly.
"""
import logging
import os
import time
from typing import Dict, List, Optional, Any

from voice_generator import VoiceGenerator
from asset_fetcher import AssetFetcher
from video_assembler import VideoAssembler
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineRunner:
    """Orchestrates the complete video generation pipeline."""
    
    def __init__(self):
        """Initialize pipeline components."""
        self.voice_generator = VoiceGenerator()
        self.asset_fetcher = AssetFetcher()
        self.video_assembler = VideoAssembler()
        
        # Validate configuration
        try:
            Config.validate_config()
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise
    
    def run_pipeline(
        self,
        text: str,
        search_terms: str,
        voice: str = None,
        randomize_voice: bool = False,
        voice_gender: str = None,
        num_images: int = 0,
        num_videos: int = 5,
        output_filename: str = None,
        enable_subtitles: bool = False,
        subtitle_text: str = None,
        subtitle_style: str = "professional",
        language: str = "en-US"
    ) -> Optional[str]:
        """Run the complete video generation pipeline.
        
        Args:
            text: Text to convert to speech
            search_terms: Search terms for visual assets
            voice: Specific voice to use (optional)
            randomize_voice: Whether to use a random voice
            voice_gender: Preferred voice gender ("male" or "female")
            num_images: Number of images to fetch
            num_videos: Number of videos to fetch
            output_filename: Output video filename
            enable_subtitles: Whether to add subtitles
            subtitle_text: Text to display as subtitles (defaults to spoken text)
            
        Returns:
            Path to generated video file, or None if failed
        """
        try:
            start_time = time.time()
            
            # Initialize pipeline
            logger.info("Pipeline components initialized successfully")
            
            # Step 1: Select voice
            selected_voice = self._select_voice(voice, randomize_voice, voice_gender)
            logger.info(f"Selected voice: {selected_voice}")
            
            # Step 2: Generate voice narration
            logger.info("Step 1: Generating voice narration...")
            # Update voice generator voice setting
            self.voice_generator.voice = selected_voice
            audio_path = self.voice_generator.generate_voice_sync(
                text=text
            )
            
            if not audio_path:
                logger.error("Voice generation failed")
                return None
            
            logger.info(f"Voice generation complete: {os.path.basename(audio_path)}")
            
            # Step 3: Fetch visual assets
            logger.info("Step 2: Fetching visual assets...")
            assets = self.asset_fetcher.download_assets_for_query(
                query=search_terms,
                max_images=num_images,
                max_videos=num_videos
            )
            images = assets.get('images', [])
            videos = assets.get('videos', [])
            
            logger.info(f"Asset fetching complete: {len(images)} images, {len(videos)} videos")
            
            # Step 4: Assemble final video
            logger.info("Step 3: Assembling final video...")
            
            # Use subtitle text if provided, otherwise use spoken text
            final_subtitle_text = subtitle_text or text if enable_subtitles else None
            
            if images or videos:
                # Create video from assets
                video_path = self.video_assembler.create_video_from_assets(
                    image_paths=images,
                    video_paths=videos,
                    audio_path=audio_path,
                    output_path=output_filename,
                    subtitle_text=final_subtitle_text,
                    enable_subtitles=enable_subtitles,
                    subtitle_style=subtitle_style
                )
            else:
                logger.warning("No assets downloaded, creating audio-only video")
                # Create simple slideshow with placeholder if no assets
                video_path = self._create_audio_only_video(
                    audio_path=audio_path,
                    output_path=output_filename,
                    subtitle_text=final_subtitle_text,
                    enable_subtitles=enable_subtitles,
                    subtitle_style=subtitle_style
                )
            
            if not video_path:
                logger.error("Video assembly failed")
                return None
            
            # Calculate execution time and file size
            end_time = time.time()
            execution_time = end_time - start_time
            file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
            
            logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Generated video: {video_path} ({file_size:,} bytes)")
            
            return video_path
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return None
    
    def _select_voice(self, voice: str = None, randomize_voice: bool = False, voice_gender: str = None) -> str:
        """Select appropriate voice based on parameters.
        
        Args:
            voice: Specific voice to use
            randomize_voice: Whether to randomize voice selection
            voice_gender: Preferred voice gender
            
        Returns:
            Selected voice name
        """
        if voice:
            # Use specific voice if provided - check across all supported languages
            all_voices = []
            for lang_info in Config.SUPPORTED_LANGUAGES.values():
                all_voices.extend(lang_info["voices"])
            
            if voice in all_voices:
                return voice
            else:
                logger.warning(f"Voice '{voice}' not found, using default")
                return Config.DEFAULT_VOICE
        
        if randomize_voice:
            # Use random voice
            if voice_gender:
                return Config.get_voice_by_gender(voice_gender)
            else:
                return Config.get_random_voice()
        
        if voice_gender:
            # Use gender-specific voice
            return Config.get_voice_by_gender(voice_gender)
        
        # Use default voice
        return Config.DEFAULT_VOICE
    
    def _create_audio_only_video(
        self,
        audio_path: str,
        output_path: str = None,
        subtitle_text: str = None,
        enable_subtitles: bool = False,
        subtitle_style: str = "professional"
    ) -> Optional[str]:
        """Create a simple audio-only video with optional subtitles.
        
        Args:
            audio_path: Path to audio file
            output_path: Output video path
            subtitle_text: Text to display as subtitles
            enable_subtitles: Whether to enable subtitles
            
        Returns:
            Path to generated video file, or None if failed
        """
        try:
            logger.info("Creating audio-only video with placeholder visuals")
            
            # Create a simple colored background
            from moviepy import ColorClip, AudioFileClip
            
            # Get audio duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create colored background
            background = ColorClip(
                size=self.video_assembler.resolution,
                color=(20, 20, 20),  # Dark gray background
                duration=duration
            )
            
            # Set audio with compatibility handling
            try:
                background = background.with_audio(audio_clip)
            except AttributeError:
                try:
                    background = background.set_audio(audio_clip)
                except AttributeError:
                    background.audio = audio_clip
            
            # Add subtitles if requested
            if enable_subtitles and subtitle_text:
                logger.info("Adding subtitles to audio-only video")
                background = self.video_assembler.add_subtitles(background, subtitle_text, enable_subtitles, subtitle_style)
            
            # Generate output path
            if output_path is None:
                output_path = os.path.join(Config.OUTPUT_DIR, "audio_only_video.mp4")
            
            # Write video
            logger.info(f"Writing audio-only video: {output_path}")
            background.write_videofile(
                output_path,
                fps=self.video_assembler.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            audio_clip.close()
            background.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio-only video creation failed: {str(e)}")
            return None
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration.
        
        Returns:
            Dictionary with pipeline information
        """
        return {
            "available_voices": Config.AVAILABLE_VOICES,
            "default_voice": Config.DEFAULT_VOICE,
            "voice_count": len(Config.AVAILABLE_VOICES),
            "male_voices": [v for v in Config.AVAILABLE_VOICES if any(name in v for name in 
                           ["Brian", "Andrew", "Guy", "Davis", "Jason", "Roger", "Steffan", "Tony", "Ryan"])],
            "female_voices": [v for v in Config.AVAILABLE_VOICES if any(name in v for name in 
                             ["Aria", "Jenny", "Ava", "Emma", "Michelle", "Nancy", "Amber", "Ashley"])],
            "resolution": Config.DEFAULT_RESOLUTION,
            "fps": Config.DEFAULT_FPS,
            "subtitle_support": True
        }


def run_simple_pipeline(
    text: str,
    search_terms: str,
    voice: str = None,
    randomize_voice: bool = False,
    output_filename: str = None,
    enable_subtitles: bool = False
) -> Optional[str]:
    """Simple function to run a pipeline without instantiating the class.
    
    Args:
        text: Text to convert to speech
        search_terms: Search terms for visual assets
        voice: Specific voice to use (optional)
        randomize_voice: Whether to use a random voice
        output_filename: Output video filename
        enable_subtitles: Whether to add subtitles
        
    Returns:
        Path to generated video file, or None if failed
    """
    try:
        runner = PipelineRunner()
        return runner.run_pipeline(
            text=text,
            search_terms=search_terms,
            voice=voice,
            randomize_voice=randomize_voice,
            output_filename=output_filename,
            enable_subtitles=enable_subtitles
        )
    except Exception as e:
        logger.error(f"Simple pipeline execution failed: {str(e)}")
        return None 