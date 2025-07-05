#!/usr/bin/env python3
"""
Main CLI interface for the AI video generator.
Provides command-line interface for running pipelines and generating videos.
"""
import click
import os
import sys
from typing import Optional

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Now import from the src directory
from pipeline_config import get_pipeline_manager
from pipeline_runner import PipelineRunner
from config import Config

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Video Generator - Create professional videos with AI voices and real stock footage."""
    pass

@cli.command()
@click.option('--pipeline', '-p', required=True, help='Pipeline name to run')
@click.option('--text', '-t', help='Custom text to override pipeline text')
@click.option('--voice', '-v', help='Specific voice to use (e.g., en-US-BrianNeural)')
@click.option('--randomize-voice', '-r', is_flag=True, help='Use a random voice')
@click.option('--voice-gender', '-g', type=click.Choice(['male', 'female']), help='Preferred voice gender')
@click.option('--subtitles', '-s', is_flag=True, help='Add subtitles to the video')
@click.option('--subtitle-text', help='Custom subtitle text (defaults to spoken text)')
@click.option('--output', '-o', help='Output filename (without extension)')
def run_pipeline(pipeline, text, voice, randomize_voice, voice_gender, subtitles, subtitle_text, output):
    """Run a video generation pipeline."""
    try:
        # Get pipeline configuration
        manager = get_pipeline_manager()
        config = manager.get_pipeline(pipeline)
        
        if not config:
            click.echo(f"❌ Pipeline '{pipeline}' not found")
            available = manager.list_pipelines()
            click.echo(f"Available pipelines: {', '.join(available)}")
            return
        
        # Display pipeline info
        click.echo(f"🎬 Running Pipeline: {pipeline}")
        click.echo(f"📝 Description: {config.description}")
        
        # Determine voice
        if voice:
            selected_voice = voice
        elif randomize_voice:
            if voice_gender:
                selected_voice = Config.get_voice_by_gender(voice_gender)
            else:
                selected_voice = Config.get_random_voice()
        elif voice_gender:
            selected_voice = Config.get_voice_by_gender(voice_gender)
        else:
            selected_voice = config.voice
        
        click.echo(f"🎤 Voice: {selected_voice}")
        
        # Set text
        final_text = text if text else config.text
        
        # Show asset info
        click.echo(f"🔍 Search: {config.search_query}")
        click.echo(f"🖼️  Assets: {config.max_images} images, {config.max_videos} videos")
        
        # Calculate estimated duration
        estimated_duration = (config.max_images * config.image_duration) + (config.max_videos * 3)
        click.echo(f"⏱️  Estimated Duration: ~{estimated_duration:.1f}s")
        
        # Show subtitle info
        if subtitles:
            click.echo(f"📄 Subtitles: Enabled")
        
        # Set output filename
        if output:
            output_filename = os.path.join(Config.OUTPUT_DIR, f"{output}.mp4")
        else:
            output_filename = os.path.join(Config.OUTPUT_DIR, config.output_filename)
        
        click.echo(f"📄 Output: {os.path.basename(output_filename)}")
        
        if text:
            click.echo(f"📄 Custom Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        click.echo()
        click.echo("🚀 Starting pipeline execution...")
        
        # Initialize and run pipeline
        runner = PipelineRunner()
        result = runner.run_pipeline(
            text=final_text,
            search_terms=config.search_query,
            voice=selected_voice,
            num_images=config.max_images,
            num_videos=config.max_videos,
            output_filename=output_filename,
            enable_subtitles=subtitles,
            subtitle_text=subtitle_text
        )
        
        if result:
            file_size = os.path.getsize(result)
            click.echo("🎉 Pipeline completed successfully!")
            click.echo(f"📹 Generated video: {os.path.basename(result)}")
            click.echo(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        else:
            click.echo("❌ Pipeline execution failed")
            click.echo("❌ Error running pipeline")
            
    except KeyboardInterrupt:
        click.echo("\n⏸️  Pipeline interrupted by user")
    except Exception as e:
        click.echo(f"❌ Pipeline execution failed")
        click.echo(f"❌ Error running pipeline: {str(e)}")

@cli.command()
def list_pipelines():
    """List all available video generation pipelines."""
    try:
        manager = get_pipeline_manager()
        pipelines = manager.get_all_pipelines()
        
        click.echo(f"🎬 Available Video Generation Pipelines ({len(pipelines)}):")
        click.echo("=" * 60)
        click.echo()
        
        for name, config in pipelines.items():
            click.echo(f"📽️  {name}")
            # Truncate long descriptions
            description = config.description
            if len(description) > 80:
                description = description[:77] + "..."
            click.echo(f"   📝 {description}")
            click.echo(f"   🔍 Search: {config.search_query}")
            click.echo(f"   🎤 Voice: {config.voice}")
            click.echo(f"   🖼️  Assets: {config.max_images} images, {config.max_videos} videos")
            
            # Calculate estimated duration
            estimated_duration = (config.max_images * config.image_duration) + (config.max_videos * 3)
            click.echo(f"   ⏱️  Duration: ~{estimated_duration:.1f}s")
            click.echo(f"   📄 Output: {config.output_filename}")
            click.echo()
        
        click.echo("💡 Usage:")
        click.echo("   python main.py run-pipeline --pipeline <name>")
        click.echo("   python main.py run-pipeline --pipeline <name> --text \"Your custom text\"")
        click.echo("   python main.py run-pipeline --pipeline <name> --randomize-voice")
        click.echo("   python main.py run-pipeline --pipeline <name> --subtitles")
        
    except Exception as e:
        click.echo(f"❌ Error listing pipelines: {str(e)}")

@cli.command()
def list_voices():
    """List all available AI voices."""
    try:
        click.echo(f"🎤 Available AI Voices ({len(Config.AVAILABLE_VOICES)}):")
        click.echo("=" * 50)
        click.echo()
        
        # Group voices by gender
        male_voices = [v for v in Config.AVAILABLE_VOICES if any(name in v for name in 
                      ["Brian", "Andrew", "Guy", "Davis", "Jason", "Roger", "Steffan", "Tony", "Ryan"])]
        female_voices = [v for v in Config.AVAILABLE_VOICES if any(name in v for name in 
                        ["Aria", "Jenny", "Ava", "Emma", "Michelle", "Nancy", "Amber", "Ashley"])]
        
        click.echo("👨 Male Voices:")
        for voice in male_voices:
            marker = "⭐" if voice == Config.DEFAULT_VOICE else "  "
            click.echo(f"   {marker} {voice}")
        
        click.echo()
        click.echo("👩 Female Voices:")
        for voice in female_voices:
            marker = "⭐" if voice == Config.DEFAULT_VOICE else "  "
            click.echo(f"   {marker} {voice}")
        
        click.echo()
        click.echo(f"⭐ Default Voice: {Config.DEFAULT_VOICE}")
        click.echo()
        click.echo("💡 Usage:")
        click.echo("   --voice en-US-BrianNeural")
        click.echo("   --randomize-voice")
        click.echo("   --voice-gender male")
        click.echo("   --voice-gender female")
        
    except Exception as e:
        click.echo(f"❌ Error listing voices: {str(e)}")

@cli.command()
@click.option('--text', '-t', required=True, help='Text to convert to speech')
@click.option('--search', '-s', required=True, help='Search terms for visual assets')
@click.option('--voice', '-v', help='Voice to use')
@click.option('--randomize-voice', '-r', is_flag=True, help='Use random voice')
@click.option('--voice-gender', '-g', type=click.Choice(['male', 'female']), help='Preferred voice gender')
@click.option('--images', '-i', default=3, help='Number of images to fetch')
@click.option('--videos', '-V', default=1, help='Number of videos to fetch')
@click.option('--output', '-o', help='Output filename (without extension)')
@click.option('--subtitles', is_flag=True, help='Add subtitles')
@click.option('--subtitle-text', help='Custom subtitle text')
def create_custom(text, search, voice, randomize_voice, voice_gender, images, videos, output, subtitles, subtitle_text):
    """Create a custom video with your own parameters."""
    try:
        # Determine voice
        if voice:
            selected_voice = voice
        elif randomize_voice:
            if voice_gender:
                selected_voice = Config.get_voice_by_gender(voice_gender)
            else:
                selected_voice = Config.get_random_voice()
        elif voice_gender:
            selected_voice = Config.get_voice_by_gender(voice_gender)
        else:
            selected_voice = Config.DEFAULT_VOICE
        
        # Set output filename
        if output:
            output_filename = os.path.join(Config.OUTPUT_DIR, f"{output}.mp4")
        else:
            output_filename = os.path.join(Config.OUTPUT_DIR, "custom_video.mp4")
        
        click.echo(f"🎬 Creating Custom Video")
        click.echo(f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        click.echo(f"🔍 Search: {search}")
        click.echo(f"🎤 Voice: {selected_voice}")
        click.echo(f"🖼️  Assets: {images} images, {videos} videos")
        click.echo(f"📄 Output: {os.path.basename(output_filename)}")
        
        if subtitles:
            click.echo(f"📄 Subtitles: Enabled")
        
        click.echo()
        click.echo("🚀 Starting video creation...")
        
        # Initialize and run pipeline
        runner = PipelineRunner()
        result = runner.run_pipeline(
            text=text,
            search_terms=search,
            voice=selected_voice,
            num_images=images,
            num_videos=videos,
            output_filename=output_filename,
            enable_subtitles=subtitles,
            subtitle_text=subtitle_text
        )
        
        if result:
            file_size = os.path.getsize(result)
            click.echo("🎉 Video creation completed successfully!")
            click.echo(f"📹 Generated video: {os.path.basename(result)}")
            click.echo(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        else:
            click.echo("❌ Video creation failed")
            
    except KeyboardInterrupt:
        click.echo("\n⏸️  Video creation interrupted by user")
    except Exception as e:
        click.echo(f"❌ Video creation failed: {str(e)}")

@cli.command()
def check_status():
    """Check system status and dependencies."""
    try:
        click.echo("🔍 Checking AI Video Generator Status...")
        click.echo("=" * 50)
        
        # Check directories
        click.echo(f"📁 Assets Directory: {Config.ASSETS_DIR}")
        click.echo(f"   {'✅ Exists' if os.path.exists(Config.ASSETS_DIR) else '❌ Missing'}")
        
        click.echo(f"📁 Output Directory: {Config.OUTPUT_DIR}")
        click.echo(f"   {'✅ Exists' if os.path.exists(Config.OUTPUT_DIR) else '❌ Missing'}")
        
        # Check API key
        click.echo(f"🔑 Pexels API Key: {'✅ Set' if Config.PEXELS_API_KEY else '❌ Not set'}")
        
        # Check pipelines
        manager = get_pipeline_manager()
        pipelines = manager.get_all_pipelines()
        click.echo(f"🎬 Available Pipelines: {len(pipelines)}")
        
        # Check voices
        click.echo(f"🎤 Available Voices: {len(Config.AVAILABLE_VOICES)}")
        
        # Check dependencies
        click.echo("\n📦 Dependencies:")
        try:
            import edge_tts
            click.echo("   ✅ edge-tts")
        except ImportError:
            click.echo("   ❌ edge-tts")
        
        try:
            import moviepy
            click.echo("   ✅ moviepy")
        except ImportError:
            click.echo("   ❌ moviepy")
        
        try:
            import requests
            click.echo("   ✅ requests")
        except ImportError:
            click.echo("   ❌ requests")
        
        try:
            import PIL
            click.echo("   ✅ Pillow")
        except ImportError:
            click.echo("   ❌ Pillow")
        
        click.echo("\n💡 If dependencies are missing, run: pip install -r requirements.txt")
        
    except Exception as e:
        click.echo(f"❌ Error checking status: {str(e)}")

if __name__ == '__main__':
    cli() 