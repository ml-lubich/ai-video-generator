"""
Pipeline configuration system for video generation scenarios.
Single responsibility: Define and manage video generation pipelines.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from config import Config


@dataclass
class PipelineConfig:
    """Configuration for a video generation pipeline."""
    
    # Content settings
    text: str
    search_query: str
    
    # Voice settings
    voice: str = "en-US-AriaNeural"
    voice_speed: str = "+0%"
    voice_pitch: str = "+0Hz"
    
    # Asset settings
    max_images: int = 3
    max_videos: int = 2
    image_duration: float = 4.0
    
    # Video settings
    output_filename: str = "generated_video.mp4"
    fps: int = 24
    resolution: tuple = (1920, 1080)
    
    # Advanced settings
    transition_duration: float = 0.5
    background_music: bool = False
    
    @property
    def description(self) -> str:
        """Get the description (same as text for backward compatibility)."""
        return self.text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline config to dictionary."""
        return {
            'text': self.text,
            'search_query': self.search_query,
            'voice': self.voice,
            'voice_speed': self.voice_speed,
            'voice_pitch': self.voice_pitch,
            'max_images': self.max_images,
            'max_videos': self.max_videos,
            'image_duration': self.image_duration,
            'output_filename': self.output_filename,
            'fps': self.fps,
            'resolution': self.resolution,
            'transition_duration': self.transition_duration,
            'background_music': self.background_music
        }


class PipelineManager:
    """Manages pre-configured video generation pipelines."""
    
    def __init__(self):
        """Initialize with built-in pipeline configurations."""
        self.pipelines = self._load_built_in_pipelines()
    
    def _load_built_in_pipelines(self) -> Dict[str, PipelineConfig]:
        """Load built-in pipeline configurations."""
        return {
            # Nature & Documentary
            "nature-documentary": PipelineConfig(
                text="Welcome to our journey through the natural world, where beauty and wonder await at every turn.",
                search_query="nature landscape forest mountains",
                voice="en-US-AriaNeural",
                max_images=4,
                max_videos=2,
                image_duration=5.0,
                output_filename="nature_documentary.mp4"
            ),
            
            "ocean-exploration": PipelineConfig(
                text="Dive into the depths of our oceans and discover the incredible marine life that calls these waters home.",
                search_query="ocean sea marine underwater life",
                voice="en-US-BrianNeural",
                max_images=3,
                max_videos=3,
                image_duration=4.5,
                output_filename="ocean_exploration.mp4"
            ),
            
            # Technology & Innovation
            "tech-innovation": PipelineConfig(
                text="Technology is revolutionizing our world, bringing innovation and progress to every aspect of our lives.",
                search_query="technology innovation digital future",
                voice="en-US-JennyNeural",
                max_images=3,
                max_videos=2,
                image_duration=3.5,
                output_filename="tech_innovation.mp4"
            ),
            
            "ai-future": PipelineConfig(
                text="Artificial intelligence is shaping our future, creating possibilities we never imagined before.",
                search_query="artificial intelligence AI technology robot",
                voice="en-US-GuyNeural",
                max_images=4,
                max_videos=1,
                image_duration=4.0,
                output_filename="ai_future.mp4"
            ),
            
            # Business & Marketing
            "business-success": PipelineConfig(
                text="Success in business comes from dedication, innovation, and the courage to pursue your dreams.",
                search_query="business success teamwork office",
                voice="en-US-AvaNeural",
                max_images=3,
                max_videos=2,
                image_duration=3.0,
                output_filename="business_success.mp4"
            ),
            
            "startup-journey": PipelineConfig(
                text="Every startup begins with an idea, a vision, and the determination to make it a reality.",
                search_query="startup entrepreneur innovation business",
                voice="en-US-AndrewNeural",
                max_images=4,
                max_videos=1,
                image_duration=3.5,
                output_filename="startup_journey.mp4"
            ),
            
            # Travel & Adventure
            "travel-adventure": PipelineConfig(
                text="Adventure awaits around every corner, from bustling cities to serene natural landscapes.",
                search_query="travel adventure city landscape culture",
                voice="en-US-EmmaNeural",
                max_images=5,
                max_videos=2,
                image_duration=3.0,
                output_filename="travel_adventure.mp4"
            ),
            
            "mountain-expedition": PipelineConfig(
                text="The mountains call to those who seek adventure, challenge, and the beauty of untamed wilderness.",
                search_query="mountain climbing hiking adventure outdoor",
                voice="en-US-BrianNeural",
                max_images=4,
                max_videos=2,
                image_duration=4.0,
                output_filename="mountain_expedition.mp4"
            ),
            
            # Health & Wellness
            "wellness-lifestyle": PipelineConfig(
                text="A healthy lifestyle is the foundation of happiness, energy, and long-term well-being.",
                search_query="health wellness fitness yoga lifestyle",
                voice="en-US-AriaNeural",
                max_images=3,
                max_videos=2,
                image_duration=4.0,
                output_filename="wellness_lifestyle.mp4"
            ),
            
            # Food & Cooking
            "culinary-journey": PipelineConfig(
                text="Food brings people together, creating memories and experiences that last a lifetime.",
                search_query="food cooking chef restaurant cuisine",
                voice="en-US-JennyNeural",
                max_images=4,
                max_videos=1,
                image_duration=3.5,
                output_filename="culinary_journey.mp4"
            ),
            
            # Quick Demo
            "quick-demo": PipelineConfig(
                text="This is a quick demonstration of our AI-powered video generation system.",
                search_query="technology demo",
                voice="en-US-AriaNeural",
                max_images=2,
                max_videos=1,
                image_duration=3.0,
                output_filename="quick_demo.mp4"
            )
        }
    
    def get_pipeline(self, name: str) -> Optional[PipelineConfig]:
        """Get a pipeline configuration by name."""
        return self.pipelines.get(name)
    
    def list_pipelines(self) -> List[str]:
        """List all available pipeline names."""
        return list(self.pipelines.keys())
    
    def get_all_pipelines(self) -> Dict[str, PipelineConfig]:
        """Get all pipeline configurations."""
        return self.pipelines.copy()
    
    def add_custom_pipeline(self, name: str, config: PipelineConfig):
        """Add a custom pipeline configuration."""
        self.pipelines[name] = config
    
    def create_custom_pipeline(
        self,
        name: str,
        text: str,
        search_query: str,
        voice: str = "en-US-AriaNeural",
        max_images: int = 3,
        max_videos: int = 2,
        image_duration: float = 4.0,
        output_filename: str = None
    ) -> PipelineConfig:
        """Create and add a custom pipeline configuration."""
        
        if output_filename is None:
            output_filename = f"{name.replace('-', '_')}.mp4"
        
        config = PipelineConfig(
            text=text,
            search_query=search_query,
            voice=voice,
            max_images=max_images,
            max_videos=max_videos,
            image_duration=image_duration,
            output_filename=output_filename
        )
        
        self.add_custom_pipeline(name, config)
        return config
    
    def get_pipeline_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a pipeline."""
        config = self.get_pipeline(name)
        if not config:
            return {}
        
        return {
            'name': name,
            'description': config.text[:100] + "..." if len(config.text) > 100 else config.text,
            'search_query': config.search_query,
            'voice': config.voice,
            'assets': f"{config.max_images} images, {config.max_videos} videos",
            'duration': f"~{(config.max_images * config.image_duration):.1f}s",
            'output': config.output_filename
        }


# Global pipeline manager instance
pipeline_manager = PipelineManager()


def get_pipeline_manager() -> PipelineManager:
    """Get the global pipeline manager instance."""
    return pipeline_manager


def list_available_pipelines() -> List[str]:
    """Quick function to list available pipelines."""
    return pipeline_manager.list_pipelines()


def get_pipeline_config(name: str) -> Optional[PipelineConfig]:
    """Quick function to get a pipeline configuration."""
    return pipeline_manager.get_pipeline(name)


if __name__ == "__main__":
    # Example usage
    manager = get_pipeline_manager()
    
    print("Available Pipelines:")
    for name in manager.list_pipelines():
        info = manager.get_pipeline_info(name)
        print(f"\n{name}:")
        print(f"  Description: {info['description']}")
        print(f"  Search Query: {info['search_query']}")
        print(f"  Voice: {info['voice']}")
        print(f"  Assets: {info['assets']}")
        print(f"  Duration: {info['duration']}")
        print(f"  Output: {info['output']}") 