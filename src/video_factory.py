"""
AI Video Factory - Master orchestrator for automated video production and publishing.
Single responsibility: Coordinate AI content generation, video creation, and YouTube publishing.
"""
import logging
import os
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from content_generator import OllamaContentGenerator, VideoContent
from pipeline_runner import PipelineRunner
from youtube_uploader import YouTubeUploader
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoFactory:
    """Automated AI video production and publishing system."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "llama3.1"):
        """Initialize the video factory.
        
        Args:
            ollama_host: Ollama server URL
            model: AI model for content generation
        """
        self.content_generator = OllamaContentGenerator(ollama_host, model)
        self.pipeline_runner = PipelineRunner()
        self.youtube_uploader = YouTubeUploader()
        
        # Factory settings
        self.settings = {
            "default_duration": 60,  # seconds
            "max_concurrent_videos": 3,
            "upload_to_youtube": False,
            "auto_publish": False,
            "schedule_interval_hours": 2,  # hours between scheduled uploads
            "max_daily_uploads": 10,
            "preferred_categories": ["technology", "science", "education"],
            "video_format": "youtube_short"
        }
        
        # Production statistics
        self.stats = {
            "videos_generated": 0,
            "videos_uploaded": 0,
            "successful_uploads": 0,
            "failed_generations": 0,
            "failed_uploads": 0,
            "total_processing_time": 0
        }
    
    def setup_systems(self) -> bool:
        """Initialize and test all subsystems.
        
        Returns:
            True if all systems ready, False if any failed
        """
        logger.info("🏭 Setting up AI Video Factory systems...")
        
        systems_ready = True
        
        # Test Ollama connection
        logger.info("🧠 Testing Ollama AI content generation...")
        if self.content_generator.test_connection():
            logger.info("✅ Ollama system ready")
        else:
            logger.error("❌ Ollama system failed")
            systems_ready = False
        
        # Test video pipeline
        logger.info("🎬 Testing video generation pipeline...")
        try:
            pipeline_info = self.pipeline_runner.get_pipeline_info()
            logger.info(f"✅ Video pipeline ready ({pipeline_info['voice_count']} voices available)")
        except Exception as e:
            logger.error(f"❌ Video pipeline failed: {str(e)}")
            systems_ready = False
        
        # Test YouTube uploader (optional)
        if self.settings["upload_to_youtube"]:
            logger.info("📺 Testing YouTube uploader...")
            if self.youtube_uploader.setup_authentication() and self.youtube_uploader.test_connection():
                logger.info("✅ YouTube uploader ready")
            else:
                logger.warning("⚠️  YouTube uploader not ready (will save videos locally)")
                self.settings["upload_to_youtube"] = False
        
        if systems_ready:
            logger.info("🎉 All systems ready! Video factory is operational.")
        else:
            logger.error("❌ Some systems failed. Check configuration.")
        
        return systems_ready
    
    def generate_single_video_with_prompt(
        self,
        prompt: str,
        category: str = None,
        duration: int = None,
        upload: bool = None,
        language: str = "en-US",
        voice_gender: str = "male"
    ) -> Optional[Dict[str, Any]]:
        """Generate a single video with a custom prompt."""
        start_time = time.time()
        
        try:
            logger.info("🎬 Starting prompt-based video generation...")
            logger.info(f"💡 Prompt: {prompt}")
            logger.info(f"📂 Category: {category or 'auto-detect'}")
            logger.info(f"⏱️  Duration: {duration or self.settings['default_duration']}s")
            logger.info(f"🌍 Language: {language}")
            logger.info(f"🎤 Voice: {voice_gender}")
            
            # Step 1: Generate AI content based on prompt
            logger.info("🧠 Step 1: Generating AI content from prompt...")
            content = self.content_generator.generate_content_from_prompt(
                prompt=prompt,
                category=category,
                duration=duration or self.settings["default_duration"],
                language=language
            )
            
            if not content:
                logger.error("❌ Failed to generate content from prompt")
                self.stats["failed_generations"] += 1
                return None
            
            logger.info(f"✅ Generated content: {content.title}")
            
            # Log the script text that will be used for audio generation
            logger.info("📝 Script text for audio generation:")
            logger.info(f"'{content.script}'")
            
            # Step 2: Create organized output folder
            logger.info("📁 Step 2: Creating organized output folder...")
            video_folder_name = self._sanitize_filename(content.title)
            video_folder_path = os.path.join("output", video_folder_name)
            os.makedirs(video_folder_path, exist_ok=True)
            
            # Save the original script text to a file
            script_file_path = os.path.join(video_folder_path, "original_script.txt")
            with open(script_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Video Title: {content.title}\n")
                f.write(f"Generated Topic: {content.topic}\n") 
                f.write(f"Language: {language}\n")
                f.write(f"Voice: {Config.get_voice_by_gender(gender=voice_gender, language=language)}\n")
                f.write(f"Search Terms: {content.search_query}\n")
                f.write(f"Duration: {duration or self.settings['default_duration']}s\n")
                f.write(f"Generated On: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n")
                f.write("ORIGINAL SCRIPT TEXT (used for audio generation):\n")
                f.write("="*50 + "\n\n")
                f.write(content.script)
            
            logger.info(f"💾 Saved original script to: {script_file_path}")
            
            # Step 3: Create video
            logger.info("🎥 Step 3: Creating video...")
            # Get appropriate voice for the language and gender
            selected_voice = Config.get_voice_by_gender(gender=voice_gender, language=language)
            
            video_path = self.pipeline_runner.run_pipeline(
                text=content.script,
                search_terms=content.search_query,
                voice=selected_voice,
                output_filename=os.path.join(video_folder_path, f"{video_folder_name}.mp4"),
                enable_subtitles=True,
                subtitle_text=content.script,
                language=language
            )
            
            if not video_path:
                logger.error("❌ Failed to create video")
                self.stats["failed_generations"] += 1
                return None
            
            logger.info(f"✅ Video created: {video_path}")
            self.stats["videos_generated"] += 1
            
            # Step 4: Upload to YouTube (if enabled)
            video_id = None
            youtube_url = None
            if upload and self.youtube_uploader.service:
                logger.info("📺 Step 4: Uploading to YouTube...")
                video_id = self.youtube_uploader.upload_video(
                    video_path=video_path,
                    title=content.title,
                    description=content.description,
                    tags=content.tags,
                    privacy_status="public" if self.settings["auto_publish"] else "unlisted"
                )
                
                if video_id:
                    logger.info(f"✅ Uploaded to YouTube: https://www.youtube.com/watch?v={video_id}")
                    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                    self.stats["successful_uploads"] += 1
                else:
                    logger.error("❌ YouTube upload failed")
                    self.stats["failed_uploads"] += 1
                
                self.stats["videos_uploaded"] += 1
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self.stats["total_processing_time"] += processing_time
            
            # Calculate file size
            file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
            
            logger.info(f"🎉 Prompt-based video generation complete in {processing_time:.1f}s")
            
            # Return result package
            return {
                "success": True,
                "video_path": video_path,
                "file_size": file_size,
                "processing_time": processing_time,
                "video_id": video_id,
                "youtube_url": youtube_url,
                "content": asdict(content),
                "stats": dict(self.stats)
            }
            
        except Exception as e:
            logger.error(f"❌ Prompt-based video generation failed: {str(e)}")
            self.stats["failed_generations"] += 1
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "stats": dict(self.stats)
            }
    
    def generate_single_video(
        self,
        category: str = None,
        duration: int = None,
        upload: bool = None,
        language: str = "en-US",
        voice_gender: str = "male"
    ) -> Optional[Dict[str, Any]]:
        """Generate a single video with AI content.
        
        Args:
            category: Content category
            duration: Video duration in seconds
            upload: Whether to upload to YouTube
            language: Video language
            voice_gender: Voice gender preference
            
        Returns:
            Dictionary with generation results or None if failed
        """
        try:
            start_time = time.time()
            duration = duration or self.settings["default_duration"]
            upload = upload if upload is not None else self.settings["upload_to_youtube"]
            
            logger.info(f"🎬 Starting single video generation...")
            logger.info(f"📂 Category: {category or 'random'}")
            logger.info(f"⏱️  Duration: {duration}s")
            logger.info(f"🌍 Language: {language}")
            logger.info(f"🎤 Voice: {voice_gender}")
            
            # Step 1: Generate AI content
            logger.info("🧠 Step 1: Generating AI content...")
            content = self.content_generator.generate_complete_content(
                category=category,
                duration=duration,
                format_type=self.settings["video_format"],
                language=language
            )
            
            if not content:
                logger.error("❌ Failed to generate AI content")
                self.stats["failed_generations"] += 1
                return None
            
            logger.info(f"✅ Generated content: {content.title}")
            
            # Log the script text that will be used for audio generation
            logger.info("📝 Script text for audio generation:")
            logger.info(f"'{content.script}'")
            
            # Step 2: Create organized output folder
            logger.info("📁 Step 2: Creating organized output folder...")
            video_folder_name = self._sanitize_filename(content.title)
            video_folder_path = os.path.join("output", video_folder_name)
            os.makedirs(video_folder_path, exist_ok=True)
            
            # Save the original script text to a file
            script_file_path = os.path.join(video_folder_path, "original_script.txt")
            with open(script_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Video Title: {content.title}\n")
                f.write(f"Generated Topic: {content.topic}\n") 
                f.write(f"Language: {language}\n")
                f.write(f"Voice: {Config.get_voice_by_gender(gender=voice_gender, language=language)}\n")
                f.write(f"Search Terms: {content.search_query}\n")
                f.write(f"Duration: {duration}s\n")
                f.write(f"Generated On: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n")
                f.write("ORIGINAL SCRIPT TEXT (used for audio generation):\n")
                f.write("="*50 + "\n\n")
                f.write(content.script)
            
            logger.info(f"💾 Saved original script to: {script_file_path}")
            
            # Step 3: Create video
            logger.info("🎥 Step 3: Creating video...")
            # Get appropriate voice for the language and gender
            selected_voice = Config.get_voice_by_gender(gender=voice_gender, language=language)
            
            video_path = self.pipeline_runner.run_pipeline(
                text=content.script,
                search_terms=content.search_query,
                voice=selected_voice,
                output_filename=os.path.join(video_folder_path, f"{video_folder_name}.mp4"),
                enable_subtitles=True,
                subtitle_text=content.script,
                language=language
            )
            
            if not video_path:
                logger.error("❌ Failed to create video")
                self.stats["failed_generations"] += 1
                return None
            
            logger.info(f"✅ Video created: {video_path}")
            self.stats["videos_generated"] += 1
            
            # Step 4: Upload to YouTube (if enabled)
            video_id = None
            if upload and self.youtube_uploader.service:
                logger.info("📺 Step 4: Uploading to YouTube...")
                video_id = self.youtube_uploader.upload_video(
                    video_path=video_path,
                    title=content.title,
                    description=content.description,
                    tags=content.tags,
                    privacy_status="public" if self.settings["auto_publish"] else "unlisted"
                )
                
                if video_id:
                    logger.info(f"✅ Uploaded to YouTube: https://www.youtube.com/watch?v={video_id}")
                    self.stats["successful_uploads"] += 1
                else:
                    logger.error("❌ YouTube upload failed")
                    self.stats["failed_uploads"] += 1
                
                self.stats["videos_uploaded"] += 1
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self.stats["total_processing_time"] += processing_time
            
            # Create result summary
            result = {
                "success": True,
                "content": asdict(content),
                "video_path": video_path,
                "video_id": video_id,
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
                "processing_time": processing_time,
                "file_size": os.path.getsize(video_path) if os.path.exists(video_path) else 0
            }
            
            logger.info(f"🎉 Single video generation complete in {processing_time:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Single video generation failed: {str(e)}")
            self.stats["failed_generations"] += 1
            return None
    
    def generate_batch_videos(
        self,
        count: int = 5,
        categories: List[str] = None,
        duration: int = None,
        upload: bool = None,
        schedule_uploads: bool = False,
        language: str = "en-US"
    ) -> List[Dict[str, Any]]:
        """Generate multiple videos in batch.
        
        Args:
            count: Number of videos to generate
            categories: List of categories to use
            duration: Video duration in seconds
            upload: Whether to upload to YouTube
            schedule_uploads: Whether to schedule uploads over time
            language: Video language
            
        Returns:
            List of generation results
        """
        logger.info(f"🏭 Starting batch generation of {count} videos")
        
        results = []
        categories = categories or self.settings["preferred_categories"]
        duration = duration or self.settings["default_duration"]
        upload = upload if upload is not None else self.settings["upload_to_youtube"]
        
        for i in range(count):
            logger.info(f"\n🎬 === Video {i+1}/{count} ===")
            
            # Select category for this video
            import random
            category = random.choice(categories) if categories else None
            
            # Generate video
            result = self.generate_single_video(
                category=category,
                duration=duration,
                upload=upload and not schedule_uploads,  # Don't upload if scheduling
                language=language
            )
            
            if result:
                results.append(result)
                
                # Schedule upload if requested
                if schedule_uploads and upload and result.get("video_path"):
                    schedule_time = datetime.now() + timedelta(hours=i * self.settings["schedule_interval_hours"])
                    logger.info(f"📅 Scheduling upload for {schedule_time}")
                    # Note: Actual scheduling would be implemented with a job scheduler
            
            # Brief pause between generations
            if i < count - 1:
                logger.info("⏸️  Brief pause before next video...")
                time.sleep(2)
        
        # Print batch summary
        successful = len([r for r in results if r.get("success")])
        total_time = sum(r.get("processing_time", 0) for r in results)
        
        logger.info(f"\n🎉 Batch generation complete!")
        logger.info(f"✅ Successful: {successful}/{count}")
        logger.info(f"⏱️  Total time: {total_time:.1f}s")
        logger.info(f"📊 Average time per video: {total_time/len(results):.1f}s" if results else "")
        
        return results
    
    def run_continuous_production(
        self,
        videos_per_day: int = 10,
        categories: List[str] = None,
        upload: bool = True
    ):
        """Run continuous video production (for long-term automation).
        
        Args:
            videos_per_day: Target videos per day
            categories: Categories to focus on
            upload: Whether to upload to YouTube
        """
        logger.info(f"🏭 Starting continuous production: {videos_per_day} videos/day")
        
        interval_hours = 24 / videos_per_day
        categories = categories or self.settings["preferred_categories"]
        
        logger.info(f"⏰ Generating video every {interval_hours:.1f} hours")
        
        try:
            while True:
                # Generate single video
                result = self.generate_single_video(
                    category=None,  # Random category
                    upload=upload
                )
                
                if result:
                    logger.info(f"✅ Production cycle complete. Next video in {interval_hours:.1f} hours")
                else:
                    logger.error("❌ Production cycle failed")
                
                # Print current stats
                self.print_stats()
                
                # Wait for next cycle
                time.sleep(interval_hours * 3600)  # Convert hours to seconds
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Continuous production stopped by user")
        except Exception as e:
            logger.error(f"❌ Continuous production failed: {str(e)}")
    
    def print_stats(self):
        """Print production statistics."""
        logger.info("\n📊 Production Statistics:")
        logger.info(f"  Videos Generated: {self.stats['videos_generated']}")
        logger.info(f"  Videos Uploaded: {self.stats['videos_uploaded']}")
        logger.info(f"  Successful Uploads: {self.stats['successful_uploads']}")
        logger.info(f"  Failed Generations: {self.stats['failed_generations']}")
        logger.info(f"  Failed Uploads: {self.stats['failed_uploads']}")
        logger.info(f"  Total Processing Time: {self.stats['total_processing_time']:.1f}s")
        
        if self.stats['videos_generated'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['videos_generated']
            logger.info(f"  Average Time per Video: {avg_time:.1f}s")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        import re
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Limit length
        return sanitized[:50]
    
    def configure_settings(self, **kwargs):
        """Update factory settings.
        
        Args:
            **kwargs: Settings to update
        """
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
                logger.info(f"Updated setting: {key} = {value}")
            else:
                logger.warning(f"Unknown setting: {key}")


def create_video_factory_cli():
    """Create CLI interface for the video factory."""
    import click
    
    factory = VideoFactory()
    
    @click.group()
    def cli():
        """AI Video Factory - Automated video production system."""
        pass
    
    @cli.command()
    def setup():
        """Set up and test all factory systems."""
        success = factory.setup_systems()
        if success:
            click.echo("🎉 Video factory is ready for production!")
        else:
            click.echo("❌ Setup failed. Check the logs for details.")
    
    @cli.command()
    @click.option('--category', help='Content category')
    @click.option('--duration', type=int, default=60, help='Video duration in seconds')
    @click.option('--upload/--no-upload', default=False, help='Upload to YouTube')
    @click.option('--language', default='en-US', help='Video language')
    def generate(category, duration, upload, language):
        """Generate a single video."""
        result = factory.generate_single_video(
            category=category,
            duration=duration,
            upload=upload,
            language=language
        )
        
        if result:
            click.echo(f"✅ Video generated: {result['video_path']}")
            if result.get('youtube_url'):
                click.echo(f"🔗 YouTube: {result['youtube_url']}")
        else:
            click.echo("❌ Video generation failed")
    
    @cli.command()
    @click.option('--count', type=int, default=5, help='Number of videos to generate')
    @click.option('--duration', type=int, default=60, help='Video duration in seconds')
    @click.option('--upload/--no-upload', default=False, help='Upload to YouTube')
    @click.option('--language', default='en-US', help='Video language')
    def batch(count, duration, upload, language):
        """Generate multiple videos in batch."""
        results = factory.generate_batch_videos(
            count=count,
            duration=duration,
            upload=upload,
            language=language
        )
        
        successful = len([r for r in results if r.get('success')])
        click.echo(f"🎉 Batch complete: {successful}/{count} videos generated")
    
    @cli.command()
    @click.option('--videos-per-day', type=int, default=10, help='Videos to generate per day')
    @click.option('--upload/--no-upload', default=True, help='Upload to YouTube')
    def continuous(videos_per_day, upload):
        """Run continuous video production."""
        factory.run_continuous_production(
            videos_per_day=videos_per_day,
            upload=upload
        )
    
    @cli.command()
    def stats():
        """Show production statistics."""
        factory.print_stats()
    
    return cli


def test_factory_integration():
    """Test the complete video factory integration."""
    try:
        factory = VideoFactory()
        
        logger.info("🧪 Testing AI Video Factory integration...")
        
        # Test system setup
        if not factory.setup_systems():
            logger.error("❌ Factory setup failed")
            return False
        
        # Test single video generation (without upload)
        logger.info("🎬 Testing single video generation...")
        result = factory.generate_single_video(
            category="technology",
            duration=30,  # Short test video
            upload=False
        )
        
        if result and result.get('success'):
            logger.info("✅ Factory integration test successful!")
            factory.print_stats()
            return True
        else:
            logger.error("❌ Factory integration test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Factory test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Create CLI interface
    cli = create_video_factory_cli()
    cli() 