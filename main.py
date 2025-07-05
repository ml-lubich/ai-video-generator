#!/usr/bin/env python3
"""
Unified Video Generator - Single entry point for all video creation.
Creates videos with custom text OR AI-generated content.
"""
import click
import os
import sys
import time
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video_factory import VideoFactory
from content_generator import OllamaContentGenerator
from pipeline_runner import PipelineRunner
from config import Config

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--text', type=str, help='Custom text for video (uses your exact script)')
@click.option('--prompt', type=str, help='AI prompt for video generation (AI expands on your idea)')
@click.option('--category', type=click.Choice(['technology', 'science', 'business', 'education', 'health', 'entertainment', 'travel', 'food', 'lifestyle', 'finance', 'art', 'sports', 'history', 'culture', 'nature', 'text']), help='Content category for AI generation')
@click.option('--length', type=int, default=60, help='Average video length in seconds (guides AI, not hard limit)')
@click.option('--language', type=str, default='en-US', help='Video language (default: en-US)')
@click.option('--voice-gender', type=click.Choice(['male', 'female', 'random']), default='male', help='Voice gender preference')
@click.option('--output', type=str, help='Output filename (without extension)')
@click.option('--subtitles/--no-subtitles', default=True, help='Enable subtitles')
@click.option('--subtitle-style', type=click.Choice(['professional', 'modern', 'cinematic']), default='professional', help='Subtitle style')
@click.option('--upload/--no-upload', default=False, help='Upload to YouTube')
@click.option('--images', type=int, default=4, help='Number of images to include')
@click.option('--videos', type=int, default=2, help='Number of video clips to include')
@click.option('--ai-model', type=str, default='llama3.2', help='AI model for content generation')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def generate_video(
    text: Optional[str],
    prompt: Optional[str],
    category: Optional[str],
    length: int,
    language: str,
    voice_gender: str,
    output: Optional[str],
    subtitles: bool,
    subtitle_style: str,
    upload: bool,
    images: int,
    videos: int,
    ai_model: str,
    verbose: bool
):
    """
    🎬 Unified Video Generator
    
    Create videos with custom text OR AI-generated content.
    
    Examples:
    
    # Custom text video
    python main.py --text "Hello world!" --category technology
    
    # AI-generated video
    python main.py --category science --length 120
    
    # Multi-language video
    python main.py --text "Bonjour!" --language fr-FR --voice-gender male
    """
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize the video creation system
        creator = UnifiedVideoCreator(ai_model=ai_model)
        
        # Determine creation mode
        if text:
            click.echo(f"🎬 Creating video with custom text...")
            mode = "custom"
        elif prompt:
            click.echo(f"🤖 Creating AI-generated video from prompt...")
            mode = "prompt"
            # Check if AI system is available
            if not creator.check_ai_system():
                click.echo("❌ AI system not available. Please provide --text for custom video.")
                return
        else:
            click.echo(f"🤖 Creating AI-generated video...")
            mode = "ai"
            # Check if AI system is available
            if not creator.check_ai_system():
                click.echo("❌ AI system not available. Please provide --text for custom video.")
                return
        
        # Display configuration
        click.echo(f"📝 Mode: {mode}")
        if prompt:
            click.echo(f"💡 Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
        click.echo(f"📂 Category: {category or 'auto-detect/random'}")
        click.echo(f"⏱️  Target length: {length}s")
        click.echo(f"🌍 Language: {language}")
        click.echo(f"🎤 Voice: {voice_gender}")
        click.echo(f"📄 Subtitles: {'✅' if subtitles else '❌'} ({subtitle_style})")
        click.echo(f"📺 Upload: {'✅' if upload else '❌'}")
        
        # Create the video
        result = creator.create_video(
            text=text,
            prompt=prompt,
            category=category,
            length=length,
            language=language,
            voice_gender=voice_gender,
            output=output,
            subtitles=subtitles,
            subtitle_style=subtitle_style,
            upload=upload,
            images=images,
            videos=videos
        )
        
        # Display results
        if result and result.get('success'):
            click.echo(f"\n🎉 Video created successfully!")
            click.echo(f"📹 Path: {result['video_path']}")
            click.echo(f"📊 Size: {result['file_size']:,} bytes")
            click.echo(f"⏱️  Time: {result['processing_time']:.1f}s")
            
            if result.get('youtube_url'):
                click.echo(f"🔗 YouTube: {result['youtube_url']}")
            
            if result.get('ai_content'):
                click.echo(f"🤖 AI Title: {result['ai_content'].get('title', 'N/A')}")
        else:
            click.echo("❌ Video creation failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\n🛑 Video creation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


class UnifiedVideoCreator:
    """Unified video creation system that handles both custom and AI content."""
    
    def __init__(self, ai_model: str = "llama3.2"):
        """Initialize the unified video creator."""
        self.ai_model = ai_model
        self.video_factory = None
        self.pipeline_runner = PipelineRunner()
        
        # Initialize AI factory only if needed
        self._ai_ready = None
    
    def check_ai_system(self) -> bool:
        """Check if AI system is available and ready."""
        if self._ai_ready is not None:
            return self._ai_ready
        
        try:
            if not self.video_factory:
                self.video_factory = VideoFactory(model=self.ai_model)
            
            # Test AI connection
            self._ai_ready = self.video_factory.content_generator.test_connection()
            return self._ai_ready
        except Exception as e:
            logger.warning(f"AI system check failed: {str(e)}")
            self._ai_ready = False
            return False
    
    def create_video(
        self,
        text: Optional[str] = None,
        prompt: Optional[str] = None,
        category: Optional[str] = None,
        length: int = 60,
        language: str = 'en-US',
        voice_gender: str = 'male',
        output: Optional[str] = None,
        subtitles: bool = True,
        subtitle_style: str = 'professional',
        upload: bool = False,
        images: int = 4,
        videos: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Create video with custom text, AI prompt, or AI-generated content.
        
        Args:
            text: Custom text (uses exact script)
            prompt: AI prompt (AI expands on your idea)
            category: Content category (optional)
            length: Target video length in seconds
            language: Video language
            voice_gender: Voice gender preference
            output: Output filename
            subtitles: Enable subtitles
            subtitle_style: Subtitle style
            upload: Upload to YouTube
            images: Number of images
            videos: Number of video clips
            
        Returns:
            Result dictionary with success status and details
        """
        start_time = time.time()
        
        try:
            # Determine content source
            if text:
                # Custom text mode
                result = self._create_custom_video(
                    text=text,
                    category=category,
                    language=language,
                    voice_gender=voice_gender,
                    output=output,
                    subtitles=subtitles,
                    subtitle_style=subtitle_style,
                    upload=upload,
                    images=images,
                    videos=videos
                )
            elif prompt:
                # AI prompt mode
                result = self._create_prompt_video(
                    prompt=prompt,
                    category=category,
                    length=length,
                    language=language,
                    voice_gender=voice_gender,
                    output=output,
                    subtitles=subtitles,
                    subtitle_style=subtitle_style,
                    upload=upload,
                    images=images,
                    videos=videos
                )
            else:
                # AI-generated mode
                result = self._create_ai_video(
                    category=category,
                    length=length,
                    language=language,
                    voice_gender=voice_gender,
                    output=output,
                    subtitles=subtitles,
                    subtitle_style=subtitle_style,
                    upload=upload,
                    images=images,
                    videos=videos
                )
            
            # Add processing time
            if result:
                result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Video creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _create_custom_video(
        self,
        text: str,
        category: Optional[str],
        language: str,
        voice_gender: str,
        output: Optional[str],
        subtitles: bool,
        subtitle_style: str,
        upload: bool,
        images: int,
        videos: int
    ) -> Dict[str, Any]:
        """Create video with custom text."""
        logger.info("Creating video with custom text")
        
        # Generate search terms from text and category
        search_terms = self._generate_search_terms(text, category)
        
        # Generate output filename if not provided
        if not output:
            output = f"custom_video_{int(time.time())}"
        
        # Use pipeline runner for custom video
        video_path = self.pipeline_runner.run_pipeline(
            text=text,
            search_terms=search_terms,
            voice=Config.get_voice_by_gender(voice_gender, language),
            output_filename=f"output/{output}.mp4",
            enable_subtitles=subtitles,
            subtitle_style=subtitle_style,
            num_images=images,
            num_videos=videos
        )
        
        if not video_path:
            return {'success': False, 'error': 'Pipeline execution failed'}
        
        # Handle YouTube upload if requested
        video_id = None
        youtube_url = None
        if upload:
            video_id, youtube_url = self._handle_youtube_upload(
                video_path=video_path,
                title=f"Custom Video - {text[:50]}...",
                description=f"Custom video created with text: {text[:200]}...",
                tags=search_terms.split() if search_terms else ['custom', 'video']
            )
        
        return {
            'success': True,
            'video_path': video_path,
            'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0,
            'video_id': video_id,
            'youtube_url': youtube_url,
            'content_type': 'custom',
            'search_terms': search_terms
        }
    
    def _create_prompt_video(
        self,
        prompt: str,
        category: Optional[str],
        length: int,
        language: str,
        voice_gender: str,
        output: Optional[str],
        subtitles: bool,
        subtitle_style: str,
        upload: bool,
        images: int,
        videos: int
    ) -> Dict[str, Any]:
        """Create video with AI prompt expansion."""
        logger.info("Creating video with AI prompt expansion")
        
        if not self.video_factory:
            self.video_factory = VideoFactory(model=self.ai_model)
        
        # Use the prompt as a custom topic for AI generation
        result = self.video_factory.generate_single_video_with_prompt(
            prompt=prompt,
            category=category,
            duration=length,
            upload=upload,
            language=language,
            voice_gender=voice_gender
        )
        
        if not result or not result.get('success'):
            return {'success': False, 'error': 'AI prompt video generation failed'}
        
        return {
            'success': True,
            'video_path': result['video_path'],
            'file_size': result['file_size'],
            'video_id': result.get('video_id'),
            'youtube_url': result.get('youtube_url'),
            'content_type': 'prompt',
            'ai_content': result.get('content'),
            'original_prompt': prompt
        }
    
    def _create_ai_video(
        self,
        category: Optional[str],
        length: int,
        language: str,
        voice_gender: str,
        output: Optional[str],
        subtitles: bool,
        subtitle_style: str,
        upload: bool,
        images: int,
        videos: int
    ) -> Dict[str, Any]:
        """Create video with AI-generated content."""
        logger.info("Creating video with AI-generated content")
        
        if not self.video_factory:
            self.video_factory = VideoFactory(model=self.ai_model)
        
        # Generate AI content
        result = self.video_factory.generate_single_video(
            category=category,
            duration=length,
            upload=upload,
            language=language,
            voice_gender=voice_gender
        )
        
        if not result or not result.get('success'):
            return {'success': False, 'error': 'AI video generation failed'}
        
        return {
            'success': True,
            'video_path': result['video_path'],
            'file_size': result['file_size'],
            'video_id': result.get('video_id'),
            'youtube_url': result.get('youtube_url'),
            'content_type': 'ai',
            'ai_content': result.get('content')
        }
    
    def _generate_search_terms(self, text: str, category: Optional[str]) -> str:
        """Generate search terms for custom text."""
        # Simple keyword extraction for search terms
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take top 5 keywords
        search_terms = ' '.join(keywords[:5])
        
        # Add category if provided
        if category:
            search_terms = f"{category} {search_terms}"
        
        return search_terms or "generic video content"
    
    def _handle_youtube_upload(self, video_path: str, title: str, description: str, tags: list) -> tuple:
        """Handle YouTube upload if configured."""
        try:
            from youtube_uploader import YouTubeUploader
            
            uploader = YouTubeUploader()
            if uploader.setup_authentication() and uploader.test_connection():
                video_id = uploader.upload_video(
                    video_path=video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    privacy_status="public"
                )
                
                if video_id:
                    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                    return video_id, youtube_url
            
            logger.warning("YouTube upload failed or not configured")
            return None, None
            
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            return None, None


# Additional utility commands
@click.group()
def cli():
    """🎬 Video Generator - Unified video creation system"""
    pass


@cli.command()
@click.option('--ai-model', default='llama3.2', help='AI model to test')
def test_systems(ai_model: str):
    """Test all video generation systems."""
    click.echo("🧪 Testing video generation systems...")
    
    creator = UnifiedVideoCreator(ai_model=ai_model)
    
    # Test basic pipeline
    click.echo("📹 Testing video pipeline...")
    try:
        # Test with minimal setup
        result = creator.create_video(
            text="This is a test video.",
            category="test",
            length=10,
            subtitles=False,
            upload=False
        )
        
        if result and result.get('success'):
            click.echo("✅ Video pipeline working")
            if os.path.exists(result['video_path']):
                click.echo(f"📁 Test video: {result['video_path']}")
        else:
            click.echo("❌ Video pipeline failed")
            
    except Exception as e:
        click.echo(f"❌ Pipeline test failed: {str(e)}")
    
    # Test AI system
    click.echo("🤖 Testing AI system...")
    if creator.check_ai_system():
        click.echo("✅ AI system ready")
    else:
        click.echo("⚠️  AI system not available (install Ollama)")
    
    click.echo("🎉 System test complete!")


@cli.command()
def list_languages():
    """List supported languages."""
    from config import Config
    
    click.echo("🌍 Supported Languages:")
    for code, info in Config.SUPPORTED_LANGUAGES.items():
        default_voice = info.get('male_voice', info.get('default_voice', 'Unknown'))
        click.echo(f"  {code}: {info['name']} (default: {default_voice})")


# Make generate_video the default command
cli.add_command(generate_video, name='create')
cli.add_command(test_systems)
cli.add_command(list_languages)

if __name__ == '__main__':
    # If no arguments provided, run the main generate_video command
    if len(sys.argv) == 1:
        generate_video(
            text=None,
            prompt=None,
            category=None,
            length=60,
            language='en-US',
            voice_gender='male',
            output=None,
            subtitles=True,
            subtitle_style='professional',
            upload=False,
            images=4,
            videos=2,
            ai_model='llama3.2',
            verbose=False
        )
    else:
        cli() 