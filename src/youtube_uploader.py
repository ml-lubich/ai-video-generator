"""
YouTube uploader module for automated video publishing.
Single responsibility: Upload videos to YouTube with metadata and scheduling.
"""
import logging
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pickle

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    # Graceful fallback if Google API libraries not installed
    print("⚠️  Google API libraries not installed. Install with:")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API scope for uploading videos
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    """Handle YouTube video uploads with authentication and metadata."""
    
    def __init__(self, credentials_file: str = "youtube_credentials.json", token_file: str = "youtube_token.pickle"):
        """Initialize YouTube uploader.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
        # Default video settings
        self.default_settings = {
            "privacy_status": "public",  # public, unlisted, private
            "category_id": "28",  # Science & Technology
            "language": "en",
            "default_audio_language": "en"
        }
        
        # YouTube categories for reference
        self.categories = {
            "Film & Animation": "1",
            "Autos & Vehicles": "2", 
            "Music": "10",
            "Pets & Animals": "15",
            "Sports": "17",
            "Travel & Events": "19",
            "Gaming": "20",
            "People & Blogs": "22",
            "Comedy": "23",
            "Entertainment": "24",
            "News & Politics": "25",
            "Howto & Style": "26",
            "Education": "27",
            "Science & Technology": "28",
            "Nonprofits & Activism": "29"
        }
    
    def setup_authentication(self) -> bool:
        """Set up YouTube API authentication.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, initiate OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("To set up YouTube API:")
                        logger.info("1. Go to https://console.developers.google.com/")
                        logger.info("2. Create a project and enable YouTube Data API v3")
                        logger.info("3. Create OAuth 2.0 credentials")
                        logger.info(f"4. Download credentials and save as {self.credentials_file}")
                        return False
                    
                    logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build YouTube service
            self.service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ YouTube API authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ YouTube authentication failed: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test YouTube API connection.
        
        Returns:
            True if connection works, False otherwise
        """
        try:
            if not self.service:
                logger.error("YouTube service not initialized")
                return False
            
            # Test with a simple API call
            response = self.service.channels().list(
                part="snippet",
                mine=True
            ).execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel_name = response['items'][0]['snippet']['title']
                logger.info(f"✅ Connected to YouTube channel: {channel_name}")
                return True
            else:
                logger.error("❌ No YouTube channel found")
                return False
                
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {str(e)}")
            return False
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        category_id: str = None,
        privacy_status: str = "public",
        thumbnail_path: str = None,
        scheduled_time: datetime = None
    ) -> Optional[str]:
        """Upload video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: Privacy setting (public, unlisted, private)
            thumbnail_path: Path to thumbnail image
            scheduled_time: Schedule video for later (requires unlisted/private)
            
        Returns:
            Video ID if successful, None if failed
        """
        try:
            if not self.service:
                logger.error("YouTube service not initialized")
                return None
            
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            # Prepare video metadata
            snippet = {
                "title": title[:100],  # YouTube title limit
                "description": description[:5000],  # YouTube description limit
                "tags": tags[:30] if tags else [],  # YouTube allows max 30 tags
                "categoryId": category_id or self.default_settings["category_id"],
                "defaultLanguage": self.default_settings["language"],
                "defaultAudioLanguage": self.default_settings["default_audio_language"]
            }
            
            status = {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
            
            # Add scheduled publish time if provided
            if scheduled_time and privacy_status in ["unlisted", "private"]:
                status["publishAt"] = scheduled_time.isoformat() + "Z"
            
            body = {
                "snippet": snippet,
                "status": status
            }
            
            # Upload video
            logger.info(f"🎬 Uploading video: {title}")
            logger.info(f"📁 File: {video_path} ({os.path.getsize(video_path):,} bytes)")
            
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload in single request
                resumable=True,
                mimetype="video/mp4"
            )
            
            request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retryable error
                        error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                        retry += 1
                        if retry > 3:
                            logger.error(f"Max retries exceeded: {error}")
                            return None
                        logger.warning(f"Retrying upload (attempt {retry}): {error}")
                    else:
                        logger.error(f"Non-retriable HTTP error: {e}")
                        return None
            
            if response:
                video_id = response['id']
                logger.info(f"✅ Video uploaded successfully!")
                logger.info(f"📹 Video ID: {video_id}")
                logger.info(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
                
                # Upload thumbnail if provided
                if thumbnail_path and os.path.exists(thumbnail_path):
                    self.upload_thumbnail(video_id, thumbnail_path)
                
                return video_id
            else:
                logger.error("❌ Upload failed: No response received")
                return None
                
        except Exception as e:
            logger.error(f"❌ Video upload failed: {str(e)}")
            return None
    
    def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload custom thumbnail for video.
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(thumbnail_path):
                logger.error(f"Thumbnail file not found: {thumbnail_path}")
                return False
            
            logger.info(f"📸 Uploading thumbnail: {thumbnail_path}")
            
            request = self.service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            
            request.execute()
            logger.info("✅ Thumbnail uploaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Thumbnail upload failed: {str(e)}")
            return False
    
    def update_video_metadata(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: List[str] = None,
        privacy_status: str = None
    ) -> bool:
        """Update video metadata after upload.
        
        Args:
            video_id: YouTube video ID
            title: New title
            description: New description
            tags: New tags
            privacy_status: New privacy status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current video details
            response = self.service.videos().list(
                part="snippet,status",
                id=video_id
            ).execute()
            
            if not response['items']:
                logger.error(f"Video not found: {video_id}")
                return False
            
            video = response['items'][0]
            snippet = video['snippet']
            status = video['status']
            
            # Update provided fields
            if title:
                snippet['title'] = title[:100]
            if description:
                snippet['description'] = description[:5000]
            if tags:
                snippet['tags'] = tags[:30]
            if privacy_status:
                status['privacyStatus'] = privacy_status
            
            # Update video
            update_request = self.service.videos().update(
                part="snippet,status",
                body={
                    'id': video_id,
                    'snippet': snippet,
                    'status': status
                }
            )
            
            update_request.execute()
            logger.info(f"✅ Video metadata updated: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update video metadata: {str(e)}")
            return False
    
    def schedule_video(self, video_id: str, publish_time: datetime) -> bool:
        """Schedule video for future publication.
        
        Args:
            video_id: YouTube video ID
            publish_time: When to publish the video
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Video must be unlisted or private to schedule
            return self.update_video_metadata(
                video_id,
                privacy_status="unlisted"  # Will be made public at scheduled time
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule video: {str(e)}")
            return False
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the authenticated channel.
        
        Returns:
            Channel information dictionary or None if failed
        """
        try:
            response = self.service.channels().list(
                part="snippet,statistics",
                mine=True
            ).execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0)
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return None


def test_youtube_integration():
    """Test function to verify YouTube API integration."""
    try:
        uploader = YouTubeUploader()
        
        # Test authentication
        if not uploader.setup_authentication():
            print("❌ YouTube authentication failed")
            print("📋 Setup steps:")
            print("1. Go to https://console.developers.google.com/")
            print("2. Create project and enable YouTube Data API v3")
            print("3. Create OAuth 2.0 credentials")
            print("4. Download and save as youtube_credentials.json")
            return False
        
        # Test connection
        if not uploader.test_connection():
            print("❌ YouTube connection test failed")
            return False
        
        # Get channel info
        channel_info = uploader.get_channel_info()
        if channel_info:
            print(f"✅ YouTube integration test successful!")
            print(f"📺 Channel: {channel_info['title']}")
            print(f"👥 Subscribers: {channel_info['subscriber_count']}")
            print(f"🎬 Videos: {channel_info['video_count']}")
            return True
        else:
            print("❌ Failed to get channel info")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_youtube_integration() 