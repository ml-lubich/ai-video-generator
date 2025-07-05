"""
AI Video Generator Package

A modular system for generating videos with AI voices and media assets.
"""

__version__ = "1.0.0"
__author__ = "Misha Lubich"
__email__ = "michaelle.lubich@gmail.com"

# Package imports for easy access
from .config import Config
from .voice_generator import VoiceGenerator
from .asset_fetcher import AssetFetcher
from .video_assembler import VideoAssembler
from .pipeline_config import PipelineConfig, PipelineManager
from .pipeline_runner import PipelineRunner

__all__ = [
    "Config",
    "VoiceGenerator", 
    "AssetFetcher",
    "VideoAssembler",
    "PipelineConfig",
    "PipelineManager",
    "PipelineRunner"
] 