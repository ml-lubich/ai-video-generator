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
    DEFAULT_LANGUAGE = "en-US"
    DEFAULT_VOICE = "en-US-BrianNeural"  # Low male voice as default
    VOICE_SPEED = "+0%"
    VOICE_PITCH = "+0Hz"
    
    # Multi-language support with male voice defaults
    SUPPORTED_LANGUAGES = {
        "en-US": {
            "name": "English (US)",
            "male_voice": "en-US-BrianNeural",
            "voices": [
                "en-US-BrianNeural", "en-US-AndrewNeural", "en-US-GuyNeural",
                "en-US-DavisNeural", "en-US-JasonNeural", "en-US-RogerNeural",
                "en-US-SteffanNeural", "en-US-TonyNeural", "en-US-RyanNeural",
                "en-US-AriaNeural", "en-US-JennyNeural", "en-US-AvaNeural",
                "en-US-EmmaNeural", "en-US-MichelleNeural", "en-US-NancyNeural",
                "en-US-AmberNeural", "en-US-AshleyNeural"
            ]
        },
        "ru-RU": {
            "name": "Russian",
            "male_voice": "ru-RU-DmitryNeural",
            "voices": ["ru-RU-DmitryNeural"]
        },
        "es-ES": {
            "name": "Spanish (Spain)",
            "male_voice": "es-ES-AlvaroNeural",
            "voices": ["es-ES-AlvaroNeural"]
        },
        "fr-FR": {
            "name": "French",
            "male_voice": "fr-FR-HenriNeural",
            "voices": ["fr-FR-HenriNeural", "fr-FR-RemyMultilingualNeural"]
        },
        "de-DE": {
            "name": "German",
            "male_voice": "de-DE-ConradNeural",
            "voices": ["de-DE-ConradNeural", "de-DE-KillianNeural", "de-DE-FlorianMultilingualNeural"]
        },
        "it-IT": {
            "name": "Italian",
            "male_voice": "it-IT-DiegoNeural",
            "voices": ["it-IT-DiegoNeural", "it-IT-GiuseppeMultilingualNeural"]
        },
        "pt-BR": {
            "name": "Portuguese (Brazil)",
            "male_voice": "pt-BR-AntonioNeural",
            "voices": ["pt-BR-AntonioNeural"]
        },
        "zh-CN": {
            "name": "Chinese (Mandarin)",
            "male_voice": "zh-CN-YunjianNeural",
            "voices": ["zh-CN-YunjianNeural", "zh-CN-YunxiNeural", "zh-CN-YunxiaNeural", "zh-CN-YunyangNeural"]
        },
        "ja-JP": {
            "name": "Japanese",
            "male_voice": "ja-JP-KeitaNeural",
            "voices": ["ja-JP-KeitaNeural"]
        },
        "ko-KR": {
            "name": "Korean",
            "male_voice": "ko-KR-InJoonNeural",
            "voices": ["ko-KR-InJoonNeural", "ko-KR-HyunsuMultilingualNeural"]
        },
        "ar-SA": {
            "name": "Arabic (Saudi Arabia)",
            "male_voice": "ar-SA-HamedNeural",
            "voices": ["ar-SA-HamedNeural"]
        },
        "hi-IN": {
            "name": "Hindi",
            "male_voice": "hi-IN-MadhurNeural",
            "voices": ["hi-IN-MadhurNeural"]
        },
        "pl-PL": {
            "name": "Polish",
            "male_voice": "pl-PL-MarekNeural",
            "voices": ["pl-PL-MarekNeural"]
        },
        "uk-UA": {
            "name": "Ukrainian",
            "male_voice": "uk-UA-OstapNeural",
            "voices": ["uk-UA-OstapNeural"]
        },
        "tr-TR": {
            "name": "Turkish",
            "male_voice": "tr-TR-AhmetNeural",
            "voices": ["tr-TR-AhmetNeural"]
        },
        "nl-NL": {
            "name": "Dutch",
            "male_voice": "nl-NL-MaartenNeural",
            "voices": ["nl-NL-MaartenNeural"]
        }
    }
    
    # Legacy support - all available voices from English (for backwards compatibility)
    AVAILABLE_VOICES = SUPPORTED_LANGUAGES["en-US"]["voices"]
    
    @classmethod
    def get_random_voice(cls, language=None):
        """Get a random voice from available voices for a specific language."""
        if language and language in cls.SUPPORTED_LANGUAGES:
            return random.choice(cls.SUPPORTED_LANGUAGES[language]["voices"])
        return random.choice(cls.AVAILABLE_VOICES)
    
    @classmethod
    def get_voice_by_gender(cls, gender="male", language=None):
        """Get a random voice by gender preference for a specific language."""
        if language and language in cls.SUPPORTED_LANGUAGES:
            voices = cls.SUPPORTED_LANGUAGES[language]["voices"]
            if gender.lower() == "male":
                # For specified language, return the default male voice
                return cls.SUPPORTED_LANGUAGES[language]["male_voice"]
            else:
                # For female, return a random voice (excluding male_voice if multiple available)
                available_voices = [v for v in voices if v != cls.SUPPORTED_LANGUAGES[language]["male_voice"]]
                return random.choice(available_voices) if available_voices else voices[0]
        else:
            # Legacy support for English
            if gender.lower() == "male":
                male_voices = [v for v in cls.AVAILABLE_VOICES if any(name in v for name in 
                              ["Brian", "Andrew", "Guy", "Davis", "Jason", "Roger", "Steffan", "Tony", "Ryan"])]
                return random.choice(male_voices)
            else:
                female_voices = [v for v in cls.AVAILABLE_VOICES if any(name in v for name in 
                               ["Aria", "Jenny", "Ava", "Emma", "Michelle", "Nancy", "Amber", "Ashley"])]
                return random.choice(female_voices)
    
    @classmethod
    def get_default_voice_for_language(cls, language):
        """Get the default male voice for a specific language."""
        if language in cls.SUPPORTED_LANGUAGES:
            return cls.SUPPORTED_LANGUAGES[language]["male_voice"]
        return cls.DEFAULT_VOICE
    
    @classmethod
    def get_supported_languages(cls):
        """Get list of supported languages with their display names."""
        return {lang: config["name"] for lang, config in cls.SUPPORTED_LANGUAGES.items()}
    
    @classmethod
    def get_voices_for_language(cls, language):
        """Get all available voices for a specific language."""
        if language in cls.SUPPORTED_LANGUAGES:
            return cls.SUPPORTED_LANGUAGES[language]["voices"]
        return cls.AVAILABLE_VOICES
    
    @classmethod
    def validate_language(cls, language):
        """Validate if a language is supported."""
        return language in cls.SUPPORTED_LANGUAGES
    
    # Video Configuration
    DEFAULT_FPS = 24
    DEFAULT_DURATION = 5  # seconds per image
    DEFAULT_RESOLUTION = (1920, 1080)
    
    # Subtitle Configuration
    SUBTITLE_FONT_SIZE = 56
    SUBTITLE_FONT_COLOR = "white"
    SUBTITLE_FONT_FAMILY = "Arial-Bold"
    SUBTITLE_POSITION = ("center", "bottom")
    SUBTITLE_MARGIN = 80
    SUBTITLE_BACKGROUND_COLOR = "black"
    SUBTITLE_BACKGROUND_OPACITY = 0.7
    SUBTITLE_STROKE_COLOR = "black"
    SUBTITLE_STROKE_WIDTH = 3
    SUBTITLE_SHADOW_OFFSET = (2, 2)
    SUBTITLE_SHADOW_COLOR = "rgba(0,0,0,0.8)"
    
    # Advanced subtitle styling
    SUBTITLE_STYLES = {
        "professional": {
            "font_family": "Arial-Bold",
            "font_size": 56,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "shadow_offset": (2, 2),
            "shadow_color": "rgba(0,0,0,0.8)"
        },
        "modern": {
            "font_family": "Helvetica-Bold",
            "font_size": 60,
            "color": "white",
            "stroke_color": "navy",
            "stroke_width": 2,
            "shadow_offset": (3, 3),
            "shadow_color": "rgba(0,0,0,0.6)"
        },
        "cinematic": {
            "font_family": "Georgia-Bold",
            "font_size": 52,
            "color": "gold",
            "stroke_color": "black",
            "stroke_width": 4,
            "shadow_offset": (2, 2),
            "shadow_color": "rgba(0,0,0,0.9)"
        }
    }
    
    # Default subtitle style
    DEFAULT_SUBTITLE_STYLE = "professional"
    
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