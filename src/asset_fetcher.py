"""
Asset fetching module for downloading images and videos from Pexels.
Single responsibility: Fetch and organize media assets from external APIs.
"""
import logging
import os
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse

import requests
from PIL import Image

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetFetcher:
    """Handles fetching images and videos from Pexels API."""
    
    def __init__(self, api_key: str = None):
        """Initialize asset fetcher with API key.
        
        Args:
            api_key: Pexels API key. If None, uses Config.PEXELS_API_KEY
        """
        self.api_key = api_key or Config.get_pexels_api_key()
        if not self.api_key:
            raise ValueError("Pexels API key is required")
        
        logger.info(f"Initializing AssetFetcher with API key: {self.api_key[:10]}...")
        
        self.headers = {
            "Authorization": f"{self.api_key}",
            "User-Agent": "VideoGenerator/1.0"
        }
        
        # Ensure asset directories exist
        Config.ensure_directories()
    
    def search_images(self, query: str, per_page: int = None) -> List[Dict]:
        """Search for images on Pexels.
        
        Args:
            query: Search query
            per_page: Number of results per page
            
        Returns:
            List of image data dictionaries
        """
        per_page = per_page or Config.ITEMS_PER_PAGE
        
        try:
            url = f"{Config.PEXELS_BASE_URL}/search"
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            
            logger.info(f"Searching images for: {query}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            images = data.get("photos", [])
            
            logger.info(f"Found {len(images)} images for '{query}'")
            return images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search images: {str(e)}")
            return []
    
    def search_videos(self, query: str, per_page: int = None) -> List[Dict]:
        """Search for videos on Pexels.
        
        Args:
            query: Search query
            per_page: Number of results per page
            
        Returns:
            List of video data dictionaries
        """
        per_page = per_page or Config.ITEMS_PER_PAGE
        
        try:
            url = f"{Config.PEXELS_VIDEOS_URL}/search"
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            
            logger.info(f"Searching videos for: {query}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("videos", [])
            
            logger.info(f"Found {len(videos)} videos for '{query}'")
            return videos
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search videos: {str(e)}")
            return []
    
    def download_image(self, image_data: Dict, filename: str = None) -> Optional[str]:
        """Download an image from Pexels data.
        
        Args:
            image_data: Image data dictionary from Pexels API
            filename: Optional filename. If None, auto-generates.
            
        Returns:
            Path to downloaded image file, or None if failed
        """
        try:
            # Get the large image URL
            image_url = image_data["src"]["large"]
            
            if filename is None:
                # Auto-generate filename
                image_id = image_data["id"]
                ext = urlparse(image_url).path.split('.')[-1]
                filename = f"image_{image_id}.{ext}"
            
            filepath = os.path.join(Config.IMAGES_DIR, filename)
            
            # Download image
            logger.info(f"Downloading image: {filename}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify and resize if needed
            self._optimize_image(filepath)
            
            logger.info(f"Image downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download image: {str(e)}")
            return None
    
    def download_video(self, video_data: Dict, filename: str = None) -> Optional[str]:
        """Download a video from Pexels data.
        
        Args:
            video_data: Video data dictionary from Pexels API
            filename: Optional filename. If None, auto-generates.
            
        Returns:
            Path to downloaded video file, or None if failed
        """
        try:
            # Get the HD video URL
            video_files = video_data["video_files"]
            # Find HD quality video
            hd_video = None
            for video_file in video_files:
                if video_file["quality"] in ["hd", "sd"]:
                    hd_video = video_file
                    break
            
            if not hd_video:
                logger.warning("No HD video found, using first available")
                hd_video = video_files[0]
            
            video_url = hd_video["link"]
            
            if filename is None:
                # Auto-generate filename
                video_id = video_data["id"]
                filename = f"video_{video_id}.mp4"
            
            filepath = os.path.join(Config.CLIPS_DIR, filename)
            
            # Download video
            logger.info(f"Downloading video: {filename}")
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Video downloaded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            return None
    
    def download_assets_for_query(self, query: str, max_images: int = 3, max_videos: int = 2) -> Dict[str, List[str]]:
        """Download both images and videos for a query.
        
        Args:
            query: Search query
            max_images: Maximum number of images to download
            max_videos: Maximum number of videos to download
            
        Returns:
            Dictionary with 'images' and 'videos' keys containing file paths
        """
        results = {"images": [], "videos": []}
        
        # Search and download images
        if max_images > 0:
            images = self.search_images(query, max_images)
            for image_data in images[:max_images]:
                filepath = self.download_image(image_data)
                if filepath:
                    results["images"].append(filepath)
                time.sleep(0.1)  # Rate limiting
        
        # Search and download videos
        if max_videos > 0:
            videos = self.search_videos(query, max_videos)
            for video_data in videos[:max_videos]:
                filepath = self.download_video(video_data)
                if filepath:
                    results["videos"].append(filepath)
                time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Downloaded {len(results['images'])} images and {len(results['videos'])} videos for '{query}'")
        return results
    
    def _optimize_image(self, filepath: str):
        """Optimize image size and format.
        
        Args:
            filepath: Path to image file
        """
        try:
            with Image.open(filepath) as img:
                # Resize if too large
                max_size = Config.DEFAULT_RESOLUTION
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
                    logger.info(f"Resized image: {filepath}")
                    
        except Exception as e:
            logger.warning(f"Failed to optimize image {filepath}: {str(e)}")


def fetch_assets_for_topic(topic: str, max_images: int = 3, max_videos: int = 2) -> Dict[str, List[str]]:
    """Utility function to quickly fetch assets for a topic.
    
    Args:
        topic: Topic to search for
        max_images: Maximum images to download
        max_videos: Maximum videos to download
        
    Returns:
        Dictionary with downloaded file paths
    """
    fetcher = AssetFetcher()
    return fetcher.download_assets_for_query(topic, max_images, max_videos)


if __name__ == "__main__":
    # Example usage
    try:
        # Test API key validation
        Config.validate_config()
        
        # Fetch some sample assets
        assets = fetch_assets_for_topic("nature", max_images=2, max_videos=1)
        print(f"Downloaded assets: {assets}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your PEXELS_API_KEY in a .env file") 