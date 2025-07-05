"""
Configuration management for the video generator.
Centralizes all settings and API keys following DRY principles.
"""
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration class for the video generator."""
    
    # API Configuration
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
    
    @classmethod
    def get_pexels_api_key(cls):
        """Get Pexels API key with fallback to environment variable."""
        return os.getenv('PEXELS_API_KEY') or cls.PEXELS_API_KEY
    
    # Voice Configuration
    DEFAULT_VOICE = "en-US-BrianNeural"  # Low male voice as default
    VOICE_SPEED = "+0%"
    VOICE_PITCH = "+0Hz"
    
    # Available voices for randomization
    AVAILABLE_VOICES = [
        # Male voices (lower pitch)
        "en-US-BrianNeural",      # Deep male
        "en-US-AndrewNeural",     # Mature male
        "en-US-GuyNeural",        # Professional male
        "en-US-DavisNeural",      # Warm male
        "en-US-JasonNeural",      # Friendly male
        
        # Female voices
        "en-US-AriaNeural",       # Clear female
        "en-US-JennyNeural",      # Expressive female
        "en-US-AvaNeural",        # Conversational female
        "en-US-EmmaNeural",       # Warm female
        "en-US-MichelleNeural",   # Professional female
        
        # Additional voices
        "en-US-NancyNeural",      # Storytelling
        "en-US-RogerNeural",      # Authoritative
        "en-US-SteffanNeural",    # Energetic
        "en-US-TonyNeural",       # Confident
        "en-US-RyanNeural",       # Casual
        "en-US-AmberNeural",      # Friendly
        "en-US-AshleyNeural",     # Expressive
    ]
    
    @classmethod
    def get_random_voice(cls):
        """Get a random voice from available voices."""
        return random.choice(cls.AVAILABLE_VOICES)
    
    @classmethod
    def get_voice_by_gender(cls, gender="male"):
        """Get a random voice by gender preference."""
        if gender.lower() == "male":
            male_voices = [v for v in cls.AVAILABLE_VOICES if any(name in v for name in 
                          ["Brian", "Andrew", "Guy", "Davis", "Jason", "Roger", "Steffan", "Tony", "Ryan"])]
            return random.choice(male_voices)
        else:
            female_voices = [v for v in cls.AVAILABLE_VOICES if any(name in v for name in 
                           ["Aria", "Jenny", "Ava", "Emma", "Michelle", "Nancy", "Amber", "Ashley"])]
            return random.choice(female_voices)
    
    # Video Configuration
    DEFAULT_FPS = 24
    DEFAULT_DURATION = 5  # seconds per image
    DEFAULT_RESOLUTION = (1920, 1080)
    
    # Subtitle Configuration
    SUBTITLE_FONT_SIZE = 48
    SUBTITLE_FONT_COLOR = "white"
    SUBTITLE_FONT_FAMILY = "Arial-Bold"
    SUBTITLE_POSITION = ("center", "bottom")
    SUBTITLE_MARGIN = 100
    SUBTITLE_BACKGROUND_COLOR = "black"
    SUBTITLE_BACKGROUND_OPACITY = 0.5
    
    # Asset Directories
    ASSETS_DIR = "assets"
    IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
    CLIPS_DIR = os.path.join(ASSETS_DIR, "clips")
    AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
    OUTPUT_DIR = "output"
    
    # Pexels API Configuration
    PEXELS_BASE_URL = "https://api.pexels.com/v1"
    PEXELS_VIDEOS_URL = "https://api.pexels.com/videos"
    ITEMS_PER_PAGE = 5
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [
            cls.ASSETS_DIR,
            cls.IMAGES_DIR,
            cls.CLIPS_DIR,
            cls.AUDIO_DIR,
            cls.OUTPUT_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        api_key = cls.get_pexels_api_key()
        if not api_key or api_key == 'your_pexels_api_key_here':
            raise ValueError("PEXELS_API_KEY is required. Please set it in your .env file.")
        
        return True 