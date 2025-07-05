"""
AI Content Generator using Ollama for topic generation and script writing.
Single responsibility: Generate engaging video content using AI.
"""
import logging
import json
import random
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoContent:
    """Structure for generated video content."""
    topic: str
    title: str
    script: str
    search_query: str
    duration_estimate: float
    tags: List[str]
    description: str
    thumbnail_query: str


class OllamaContentGenerator:
    """Generate video content using Ollama AI models."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "llama3.2"):
        """Initialize the content generator.
        
        Args:
            ollama_host: Ollama server URL
            model: AI model to use for generation
        """
        self.ollama_host = ollama_host
        self.model = model
        self.session = requests.Session()
        
        # Content categories for diverse video generation
        self.categories = [
            "technology", "nature", "science", "travel", "business",
            "health", "food", "entertainment", "education", "lifestyle",
            "finance", "art", "sports", "history", "culture"
        ]
        
        # Video formats for different platforms
        self.formats = {
            "youtube_short": {"duration": 60, "aspect": "vertical"},
            "youtube_video": {"duration": 300, "aspect": "horizontal"}, 
            "instagram_reel": {"duration": 30, "aspect": "vertical"},
            "tiktok": {"duration": 15, "aspect": "vertical"}
        }
    
    def test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = self.session.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                logger.info(f"✅ Connected to Ollama at {self.ollama_host}")
                return True
            else:
                logger.error(f"❌ Ollama connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to Ollama: {str(e)}")
            return False
    
    def generate_with_ollama(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Generate text using Ollama API.
        
        Args:
            prompt: Text prompt for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = self.session.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate with Ollama: {str(e)}")
            return None
    
    def generate_topic(self, category: str = None) -> Optional[str]:
        """Generate a trending video topic.
        
        Args:
            category: Optional category to focus on
            
        Returns:
            Generated topic or None if failed
        """
        try:
            # Use specific category or pick random one
            selected_category = category or random.choice(self.categories)
            
            prompt = f"""Generate a trending, engaging video topic about {selected_category} that would be perfect for YouTube or social media. 

Requirements:
- Current and relevant to 2024
- Engaging and clickable
- Suitable for a 1-3 minute video
- Educational or entertaining
- Avoids controversial topics

Return ONLY the topic title, nothing else.

Example: "How AI is Revolutionizing Modern Photography"
Topic:"""

            topic = self.generate_with_ollama(prompt, max_tokens=100)
            
            if topic and len(topic) > 10:
                logger.info(f"Generated topic: {topic}")
                return topic
            else:
                logger.warning("Generated topic too short or empty")
                return None
                
        except Exception as e:
            logger.error(f"Topic generation failed: {str(e)}")
            return None
    
    def generate_script(self, topic: str, duration: int = 60) -> Optional[str]:
        """Generate video script for the given topic.
        
        Args:
            topic: Video topic
            duration: Target duration in seconds
            
        Returns:
            Generated script or None if failed
        """
        try:
            # Estimate words per minute (average 150-180 WPM for video)
            target_words = int((duration / 60) * 160)
            
            prompt = f"""Write an engaging video script about: {topic}

Requirements:
- Target length: {target_words} words (for {duration} seconds)
- Conversational and engaging tone
- Hook viewers in first 5 seconds
- Include specific facts or insights
- End with a call to engagement
- Write in first person as narrator
- NO stage directions or camera notes
- Just the spoken narration text

Script:"""

            script = self.generate_with_ollama(prompt, max_tokens=target_words + 100)
            
            if script and len(script.split()) > 20:
                logger.info(f"Generated script: {len(script.split())} words")
                return script
            else:
                logger.warning("Generated script too short")
                return None
                
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            return None
    
    def generate_search_query(self, topic: str) -> Optional[str]:
        """Generate search terms for visual assets.
        
        Args:
            topic: Video topic
            
        Returns:
            Search query string or None if failed
        """
        try:
            prompt = f"""For the video topic: {topic}

Generate 3-5 search keywords that would find the best stock photos and videos for this content.

Requirements:
- Focus on visual elements that support the topic
- Use specific, searchable terms
- Avoid abstract concepts
- Prioritize concrete objects, places, or activities

Return ONLY the search terms separated by spaces.

Example: "artificial intelligence robot technology computer"
Search terms:"""

            search_query = self.generate_with_ollama(prompt, max_tokens=50)
            
            if search_query and len(search_query) > 5:
                # Clean up the search query
                search_query = ' '.join(search_query.split())
                logger.info(f"Generated search query: {search_query}")
                return search_query
            else:
                logger.warning("Generated search query too short")
                return None
                
        except Exception as e:
            logger.error(f"Search query generation failed: {str(e)}")
            return None
    
    def generate_metadata(self, topic: str, script: str) -> Dict[str, Any]:
        """Generate video metadata (title, description, tags).
        
        Args:
            topic: Video topic
            script: Video script
            
        Returns:
            Dictionary with metadata
        """
        try:
            prompt = f"""For this video:
Topic: {topic}
Script: {script[:500]}...

Generate YouTube metadata in JSON format:

{{
    "title": "Optimized YouTube title (under 60 chars)",
    "description": "Engaging description (2-3 sentences)", 
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

Requirements:
- Title should be catchy and SEO-friendly
- Description should summarize value
- Tags should be relevant and searchable
- Return valid JSON only"""

            metadata_text = self.generate_with_ollama(prompt, max_tokens=300)
            
            if metadata_text:
                try:
                    # Try to parse JSON
                    metadata = json.loads(metadata_text)
                    logger.info("Generated metadata successfully")
                    return metadata
                except json.JSONDecodeError:
                    logger.warning("Failed to parse metadata JSON, using defaults")
                    return self._fallback_metadata(topic)
            else:
                return self._fallback_metadata(topic)
                
        except Exception as e:
            logger.error(f"Metadata generation failed: {str(e)}")
            return self._fallback_metadata(topic)
    
    def _fallback_metadata(self, topic: str) -> Dict[str, Any]:
        """Generate fallback metadata when AI generation fails."""
        return {
            "title": topic[:60],
            "description": f"Learn about {topic.lower()} in this informative video.",
            "tags": topic.lower().split()[:5]
        }
    
    def generate_complete_content(
        self, 
        category: str = None, 
        duration: int = 60,
        format_type: str = "youtube_short"
    ) -> Optional[VideoContent]:
        """Generate complete video content package.
        
        Args:
            category: Content category
            duration: Target duration in seconds
            format_type: Video format type
            
        Returns:
            VideoContent object or None if failed
        """
        try:
            logger.info(f"🎬 Generating complete video content for {format_type}")
            
            # Step 1: Generate topic
            topic = self.generate_topic(category)
            if not topic:
                logger.error("Failed to generate topic")
                return None
            
            # Step 2: Generate script
            script = self.generate_script(topic, duration)
            if not script:
                logger.error("Failed to generate script")
                return None
            
            # Step 3: Generate search query
            search_query = self.generate_search_query(topic)
            if not search_query:
                logger.error("Failed to generate search query")
                return None
            
            # Step 4: Generate metadata
            metadata = self.generate_metadata(topic, script)
            
            # Step 5: Create content package
            content = VideoContent(
                topic=topic,
                title=metadata.get("title", topic),
                script=script,
                search_query=search_query,
                duration_estimate=duration,
                tags=metadata.get("tags", []),
                description=metadata.get("description", ""),
                thumbnail_query=search_query.split()[0] if search_query else "generic"
            )
            
            logger.info(f"✅ Generated complete content package: {content.title}")
            return content
            
        except Exception as e:
            logger.error(f"Complete content generation failed: {str(e)}")
            return None
    
    def generate_batch_content(
        self, 
        count: int = 5,
        categories: List[str] = None,
        duration: int = 60
    ) -> List[VideoContent]:
        """Generate multiple video content packages.
        
        Args:
            count: Number of videos to generate
            categories: List of categories to use
            duration: Target duration for each video
            
        Returns:
            List of VideoContent objects
        """
        logger.info(f"🎬 Generating batch of {count} video content packages")
        
        content_list = []
        categories = categories or self.categories
        
        for i in range(count):
            category = random.choice(categories)
            content = self.generate_complete_content(category, duration)
            
            if content:
                content_list.append(content)
                logger.info(f"✅ Generated content {i+1}/{count}: {content.title}")
            else:
                logger.warning(f"❌ Failed to generate content {i+1}/{count}")
        
        logger.info(f"🎉 Batch generation complete: {len(content_list)}/{count} successful")
        return content_list


def test_ollama_integration():
    """Test function to verify Ollama integration."""
    try:
        generator = OllamaContentGenerator()
        
        # Test connection
        if not generator.test_connection():
            print("❌ Cannot connect to Ollama. Make sure it's running:")
            print("   curl -fsSL https://ollama.ai/install.sh | sh")
            print("   ollama serve")
            print("   ollama pull llama3.2")
            return False
        
        # Test content generation
        print("🧪 Testing content generation...")
        content = generator.generate_complete_content("technology", 60)
        
        if content:
            print(f"✅ Test successful!")
            print(f"📝 Topic: {content.topic}")
            print(f"🎬 Title: {content.title}")
            print(f"🔍 Search: {content.search_query}")
            print(f"📄 Script: {content.script[:100]}...")
            return True
        else:
            print("❌ Content generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_ollama_integration() 