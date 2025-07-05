"""
Voice generation module using edge-tts for AI voice synthesis.
Single responsibility: Generate natural-sounding AI voice from text.
"""
import asyncio
import logging
import os
from typing import Optional

import edge_tts

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceGenerator:
    """Handles AI voice generation using Microsoft Edge TTS."""
    
    def __init__(self, voice: str = None, speed: str = None, pitch: str = None):
        """Initialize the voice generator with optional voice settings.
        
        Args:
            voice: Voice name (e.g., "en-US-AriaNeural")
            speed: Voice speed adjustment (e.g., "+0%", "+10%", "-10%")
            pitch: Voice pitch adjustment (e.g., "+0Hz", "+10Hz", "-10Hz")
        """
        self.voice = voice or Config.DEFAULT_VOICE
        self.speed = speed or Config.VOICE_SPEED
        self.pitch = pitch or Config.VOICE_PITCH
        
        # Ensure audio directory exists
        Config.ensure_directories()
    
    async def synthesize_text(self, text: str, output_file: str = None) -> str:
        """Generate voice audio from text.
        
        Args:
            text: The text to synthesize
            output_file: Optional output filename. If None, auto-generates.
            
        Returns:
            Path to the generated audio file
            
        Raises:
            ValueError: If text is empty
            RuntimeError: If synthesis fails
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        if output_file is None:
            # Auto-generate filename based on text hash
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_file = os.path.join(Config.AUDIO_DIR, f"voice_{text_hash}.mp3")
        
        try:
            logger.info(f"Synthesizing text with voice: {self.voice}")
            logger.info(f"Text preview: {text[:50]}...")
            
            # Create edge-tts communicate object
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.speed,
                pitch=self.pitch
            )
            
            # Save audio file
            await communicate.save(output_file)
            
            logger.info(f"Voice synthesis complete: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Voice synthesis failed: {str(e)}")
            raise RuntimeError(f"Failed to synthesize voice: {str(e)}")
    
    def generate_voice_sync(self, text: str, output_file: str = None) -> str:
        """Synchronous wrapper for voice generation.
        
        Args:
            text: The text to synthesize
            output_file: Optional output filename
            
        Returns:
            Path to the generated audio file
        """
        return asyncio.run(self.synthesize_text(text, output_file))
    
    @staticmethod
    async def list_available_voices() -> list:
        """Get list of available voices from edge-tts.
        
        Returns:
            List of available voice names
        """
        try:
            voices = await edge_tts.list_voices()
            return [voice["Name"] for voice in voices]
        except Exception as e:
            logger.error(f"Failed to list voices: {str(e)}")
            return []
    
    @staticmethod
    def get_available_voices_sync() -> list:
        """Synchronous wrapper for getting available voices."""
        return asyncio.run(VoiceGenerator.list_available_voices())


def create_voice_from_text(text: str, output_file: str = None, voice: str = None) -> str:
    """Utility function to quickly generate voice from text.
    
    Args:
        text: Text to synthesize
        output_file: Output filename (optional)
        voice: Voice name (optional)
        
    Returns:
        Path to generated audio file
    """
    generator = VoiceGenerator(voice=voice)
    return generator.generate_voice_sync(text, output_file)


if __name__ == "__main__":
    # Example usage
    sample_text = "Welcome to our AI-powered video generator. This is a test of the voice synthesis system."
    
    try:
        audio_file = create_voice_from_text(sample_text)
        print(f"Generated voice file: {audio_file}")
        
        # List available voices
        voices = VoiceGenerator.get_available_voices_sync()
        print(f"Available voices: {len(voices)} found")
        
    except Exception as e:
        print(f"Error: {e}") 