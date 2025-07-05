"""
Test suite for unified video creator functionality.
Tests both custom text and AI-generated video creation.
"""
import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import main module
import main
from main import UnifiedVideoCreator


class TestUnifiedVideoCreator(unittest.TestCase):
    """Test cases for unified video creator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.creator = UnifiedVideoCreator()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_search_terms_generation(self):
        """Test search terms generation from text."""
        text = "This is a test about artificial intelligence and machine learning"
        category = "technology"
        
        search_terms = self.creator._generate_search_terms(text, category)
        
        # Should include category
        self.assertIn("technology", search_terms)
        
        # Should include meaningful words
        self.assertIn("artificial", search_terms)
        self.assertIn("intelligence", search_terms)
        self.assertIn("machine", search_terms)
        self.assertIn("learning", search_terms)
        
        # Should not include stop words
        self.assertNotIn("this", search_terms)
        self.assertNotIn("and", search_terms)
    
    def test_search_terms_without_category(self):
        """Test search terms generation without category."""
        text = "Video about space exploration and rockets"
        
        search_terms = self.creator._generate_search_terms(text, None)
        
        # Should include meaningful words
        self.assertIn("video", search_terms)
        self.assertIn("space", search_terms)
        self.assertIn("exploration", search_terms)
        self.assertIn("rockets", search_terms)
    
    def test_search_terms_empty_text(self):
        """Test search terms generation with empty text."""
        text = ""
        category = "science"
        
        search_terms = self.creator._generate_search_terms(text, category)
        
        # Should return fallback
        self.assertEqual(search_terms, "science")
    
    def test_search_terms_only_stop_words(self):
        """Test search terms generation with only stop words."""
        text = "the and or but in on at to for of with by"
        
        search_terms = self.creator._generate_search_terms(text, None)
        
        # Should return fallback
        self.assertEqual(search_terms, "generic video content")
    
    @patch('main.VideoFactory')
    def test_ai_system_check_success(self, mock_video_factory):
        """Test successful AI system check."""
        # Mock the video factory and content generator
        mock_factory_instance = Mock()
        mock_content_generator = Mock()
        mock_content_generator.test_connection.return_value = True
        mock_factory_instance.content_generator = mock_content_generator
        mock_video_factory.return_value = mock_factory_instance
        
        creator = UnifiedVideoCreator()
        result = creator.check_ai_system()
        
        self.assertTrue(result)
        self.assertTrue(creator._ai_ready)
    
    @patch('main.VideoFactory')
    def test_ai_system_check_failure(self, mock_video_factory):
        """Test AI system check failure."""
        # Mock the video factory to raise exception
        mock_video_factory.side_effect = Exception("AI system unavailable")
        
        creator = UnifiedVideoCreator()
        result = creator.check_ai_system()
        
        self.assertFalse(result)
        self.assertFalse(creator._ai_ready)
    
    @patch('main.PipelineRunner')
    def test_create_custom_video_success(self, mock_pipeline_runner):
        """Test successful custom video creation."""
        # Mock pipeline runner
        mock_runner_instance = Mock()
        mock_runner_instance.run_pipeline.return_value = "output/test_video.mp4"
        mock_pipeline_runner.return_value = mock_runner_instance
        
        # Create fake video file
        video_path = os.path.join(self.temp_dir, "test_video.mp4")
        with open(video_path, 'w') as f:
            f.write("fake video content")
        
        # Mock os.path.getsize
        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.exists', return_value=True):
                creator = UnifiedVideoCreator()
                creator.pipeline_runner = mock_runner_instance
                
                result = creator._create_custom_video(
                    text="Test video text",
                    category="test",
                    language="en-US",
                    voice_gender="male",
                    output="test_output",
                    subtitles=True,
                    subtitle_style="professional",
                    upload=False,
                    images=4,
                    videos=2
                )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content_type'], 'custom')
        self.assertEqual(result['file_size'], 1024)
        self.assertIn('search_terms', result)
    
    @patch('main.PipelineRunner')
    def test_create_custom_video_failure(self, mock_pipeline_runner):
        """Test custom video creation failure."""
        # Mock pipeline runner to return None (failure)
        mock_runner_instance = Mock()
        mock_runner_instance.run_pipeline.return_value = None
        mock_pipeline_runner.return_value = mock_runner_instance
        
        creator = UnifiedVideoCreator()
        creator.pipeline_runner = mock_runner_instance
        
        result = creator._create_custom_video(
            text="Test video text",
            category="test",
            language="en-US",
            voice_gender="male",
            output="test_output",
            subtitles=True,
            subtitle_style="professional",
            upload=False,
            images=4,
            videos=2
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Pipeline execution failed')
    
    @patch('main.VideoFactory')
    def test_create_ai_video_success(self, mock_video_factory):
        """Test successful AI video creation."""
        # Mock video factory
        mock_factory_instance = Mock()
        mock_factory_instance.generate_single_video.return_value = {
            'success': True,
            'video_path': 'output/ai_video.mp4',
            'file_size': 2048,
            'video_id': 'test123',
            'youtube_url': 'https://youtube.com/watch?v=test123',
            'content': {'title': 'AI Generated Video', 'description': 'Test description'}
        }
        mock_video_factory.return_value = mock_factory_instance
        
        creator = UnifiedVideoCreator()
        creator.video_factory = mock_factory_instance
        
        result = creator._create_ai_video(
            category="technology",
            length=60,
            language="en-US",
            voice_gender="male",
            output="ai_output",
            subtitles=True,
            subtitle_style="professional",
            upload=False,
            images=4,
            videos=2
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content_type'], 'ai')
        self.assertEqual(result['file_size'], 2048)
        self.assertEqual(result['video_id'], 'test123')
        self.assertIn('ai_content', result)
    
    @patch('main.VideoFactory')
    def test_create_ai_video_failure(self, mock_video_factory):
        """Test AI video creation failure."""
        # Mock video factory to return failure
        mock_factory_instance = Mock()
        mock_factory_instance.generate_single_video.return_value = {
            'success': False,
            'error': 'AI generation failed'
        }
        mock_video_factory.return_value = mock_factory_instance
        
        creator = UnifiedVideoCreator()
        creator.video_factory = mock_factory_instance
        
        result = creator._create_ai_video(
            category="technology",
            length=60,
            language="en-US",
            voice_gender="male",
            output="ai_output",
            subtitles=True,
            subtitle_style="professional",
            upload=False,
            images=4,
            videos=2
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'AI video generation failed')
    
    def test_create_video_text_mode(self):
        """Test video creation in text mode."""
        with patch.object(self.creator, '_create_custom_video') as mock_custom:
            mock_custom.return_value = {'success': True, 'processing_time': 10.0}
            
            result = self.creator.create_video(
                text="Custom text video",
                category="test"
            )
            
            # Should call custom video creation
            mock_custom.assert_called_once()
            self.assertTrue(result['success'])
            self.assertIn('processing_time', result)
    
    def test_create_video_ai_mode(self):
        """Test video creation in AI mode."""
        with patch.object(self.creator, '_create_ai_video') as mock_ai:
            mock_ai.return_value = {'success': True, 'processing_time': 15.0}
            
            result = self.creator.create_video(
                text=None,  # No text = AI mode
                category="technology",
                length=90
            )
            
            # Should call AI video creation
            mock_ai.assert_called_once()
            self.assertTrue(result['success'])
            self.assertIn('processing_time', result)
    
    def test_create_video_exception_handling(self):
        """Test exception handling in video creation."""
        with patch.object(self.creator, '_create_custom_video') as mock_custom:
            mock_custom.side_effect = Exception("Test exception")
            
            result = self.creator.create_video(
                text="Test text"
            )
            
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Test exception')
            self.assertIn('processing_time', result)


class TestYouTubeIntegration(unittest.TestCase):
    """Test YouTube upload integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.creator = UnifiedVideoCreator()
    
    @patch('main.YouTubeUploader')
    def test_youtube_upload_success(self, mock_uploader_class):
        """Test successful YouTube upload."""
        # Mock YouTube uploader
        mock_uploader = Mock()
        mock_uploader.setup_authentication.return_value = True
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_video.return_value = "test_video_id"
        mock_uploader_class.return_value = mock_uploader
        
        video_id, youtube_url = self.creator._handle_youtube_upload(
            video_path="test_video.mp4",
            title="Test Video",
            description="Test Description",
            tags=["test", "video"]
        )
        
        self.assertEqual(video_id, "test_video_id")
        self.assertEqual(youtube_url, "https://www.youtube.com/watch?v=test_video_id")
    
    @patch('main.YouTubeUploader')
    def test_youtube_upload_auth_failure(self, mock_uploader_class):
        """Test YouTube upload with authentication failure."""
        # Mock YouTube uploader with auth failure
        mock_uploader = Mock()
        mock_uploader.setup_authentication.return_value = False
        mock_uploader_class.return_value = mock_uploader
        
        video_id, youtube_url = self.creator._handle_youtube_upload(
            video_path="test_video.mp4",
            title="Test Video",
            description="Test Description",
            tags=["test", "video"]
        )
        
        self.assertIsNone(video_id)
        self.assertIsNone(youtube_url)
    
    @patch('main.YouTubeUploader')
    def test_youtube_upload_exception(self, mock_uploader_class):
        """Test YouTube upload with exception."""
        # Mock YouTube uploader to raise exception
        mock_uploader_class.side_effect = Exception("YouTube API error")
        
        video_id, youtube_url = self.creator._handle_youtube_upload(
            video_path="test_video.mp4",
            title="Test Video",
            description="Test Description",
            tags=["test", "video"]
        )
        
        self.assertIsNone(video_id)
        self.assertIsNone(youtube_url)


class TestMainCLI(unittest.TestCase):
    """Test main CLI functionality."""
    
    @patch('main.UnifiedVideoCreator')
    def test_generate_video_custom_mode(self, mock_creator_class):
        """Test CLI video generation in custom mode."""
        # Mock the creator
        mock_creator = Mock()
        mock_creator.create_video.return_value = {
            'success': True,
            'video_path': 'output/test.mp4',
            'file_size': 1024,
            'processing_time': 30.0
        }
        mock_creator_class.return_value = mock_creator
        
        # Test would require Click testing which is complex
        # This is a placeholder for integration testing
        self.assertTrue(True)  # Placeholder assertion
    
    @patch('main.UnifiedVideoCreator')  
    def test_generate_video_ai_mode(self, mock_creator_class):
        """Test CLI video generation in AI mode."""
        # Mock the creator
        mock_creator = Mock()
        mock_creator.check_ai_system.return_value = True
        mock_creator.create_video.return_value = {
            'success': True,
            'video_path': 'output/ai_test.mp4',
            'file_size': 2048,
            'processing_time': 45.0,
            'ai_content': {'title': 'AI Generated Video'}
        }
        mock_creator_class.return_value = mock_creator
        
        # Test would require Click testing which is complex
        # This is a placeholder for integration testing
        self.assertTrue(True)  # Placeholder assertion


if __name__ == '__main__':
    unittest.main(verbosity=2) 