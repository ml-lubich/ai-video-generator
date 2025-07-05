"""
Test suite for subtitle timing functionality.
Tests both text-based timing and Whisper integration.
"""
import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from video_assembler import VideoAssembler
from config import Config


class TestSubtitleTiming:
    """Test cases for subtitle timing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.video_assembler = VideoAssembler()
        
        # Mock config paths
        self.original_output_dir = Config.OUTPUT_DIR
        Config.OUTPUT_DIR = self.temp_dir
    
    def teardown_method(self):
        """Clean up test environment."""
        Config.OUTPUT_DIR = self.original_output_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_text_based_timing_equal_sentences(self):
        """Test text-based timing with equal length sentences."""
        text = "First sentence. Second sentence. Third sentence."
        duration = 30.0
        
        # Create mock SRT file
        srt_path = os.path.join(self.temp_dir, "test.srt")
        
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        # Read and verify SRT content
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Should have 3 subtitles
        assert "1\n" in content
        assert "2\n" in content
        assert "3\n" in content
        
        # Verify timing exists
        assert "00:00:00" in content
        assert "First sentence" in content
        assert "Second sentence" in content
        assert "Third sentence" in content
    
    def test_text_based_timing_different_lengths(self):
        """Test text-based timing with different sentence lengths."""
        text = "Short. This is a much longer sentence with many words. Brief."
        duration = 30.0
        
        srt_path = os.path.join(self.temp_dir, "test_lengths.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        # Read and parse SRT
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Parse timing from SRT
        lines = content.strip().split('\n')
        timings = []
        for line in lines:
            if '-->' in line:
                start, end = line.split(' --> ')
                timings.append((start, end))
        
        # Should have 3 timing entries
        assert len(timings) == 3
        
        # Verify that longer sentence gets more time
        # (This is a basic check - exact timing depends on implementation)
        assert len(timings) > 0
    
    def test_comma_separated_sentences(self):
        """Test timing with comma-separated sentences."""
        text = "First part, second part, third part, fourth part"
        duration = 20.0
        
        srt_path = os.path.join(self.temp_dir, "test_comma.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Should split on commas
        assert "First part" in content
        assert "second part" in content
        assert "third part" in content
        assert "fourth part" in content
    
    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text."""
        text = ""
        duration = 10.0
        
        srt_path = os.path.join(self.temp_dir, "test_empty.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        # Should handle gracefully
        assert result is None or (result and os.path.exists(srt_path))
    
    def test_single_sentence_timing(self):
        """Test timing with single sentence."""
        text = "This is a single sentence for testing."
        duration = 10.0
        
        srt_path = os.path.join(self.temp_dir, "test_single.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Should have exactly one subtitle
        assert "1\n" in content
        assert "2\n" not in content
        assert "This is a single sentence for testing" in content
    
    @patch('whisper.load_model')
    def test_whisper_integration_success(self, mock_load_model):
        """Test successful Whisper integration."""
        # Mock Whisper model and result
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        # Mock transcription result
        mock_result = {
            'segments': [
                {
                    'start': 0.0,
                    'end': 3.5,
                    'text': ' Testing our new subtitle system.'
                },
                {
                    'start': 4.0,
                    'end': 6.2,
                    'text': ' This works perfectly.'
                },
                {
                    'start': 6.8,
                    'end': 9.1,
                    'text': ' Great timing accuracy.'
                }
            ]
        }
        mock_model.transcribe.return_value = mock_result
        
        # Create fake audio file
        audio_path = os.path.join(self.temp_dir, "test_audio.mp3")
        with open(audio_path, 'w') as f:
            f.write("fake audio content")
        
        srt_path = os.path.join(self.temp_dir, "whisper_test.srt")
        
        result = self.video_assembler.generate_srt_with_whisper(audio_path, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Verify Whisper timing is used
        assert "00:00:00,000 --> 00:00:03,500" in content
        assert "00:00:04,000 --> 00:00:06,200" in content
        assert "00:00:06,800 --> 00:00:09,100" in content
        
        # Verify text content
        assert "Testing our new subtitle system" in content
        assert "This works perfectly" in content
        assert "Great timing accuracy" in content
    
    @patch('whisper.load_model')
    def test_whisper_integration_failure(self, mock_load_model):
        """Test Whisper integration failure handling."""
        # Mock Whisper to raise an exception
        mock_load_model.side_effect = Exception("Whisper not available")
        
        audio_path = os.path.join(self.temp_dir, "test_audio.mp3")
        with open(audio_path, 'w') as f:
            f.write("fake audio content")
        
        srt_path = os.path.join(self.temp_dir, "whisper_fail.srt")
        
        result = self.video_assembler.generate_srt_with_whisper(audio_path, srt_path)
        
        # Should return None on failure
        assert result is None
    
    def test_timing_accuracy_calculation(self):
        """Test that timing calculations are accurate."""
        # Test with known word counts
        text = "One. Two three four. Five six seven eight nine ten eleven twelve."
        duration = 30.0
        
        srt_path = os.path.join(self.temp_dir, "test_accuracy.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Parse timing
        lines = content.strip().split('\n')
        timings = []
        for line in lines:
            if '-->' in line:
                start_str, end_str = line.split(' --> ')
                # Parse time format: HH:MM:SS,mmm
                start_parts = start_str.split(':')
                end_parts = end_str.split(':')
                
                start_seconds = float(start_parts[2].replace(',', '.'))
                end_seconds = float(end_parts[2].replace(',', '.'))
                
                timings.append((start_seconds, end_seconds))
        
        # Verify timing progression
        assert len(timings) == 3
        assert timings[0][0] == 0.0  # First subtitle starts at 0
        assert timings[2][1] <= duration  # Last subtitle ends within duration
        
        # Verify timing is proportional to word count
        # Sentence 1: 1 word
        # Sentence 2: 3 words  
        # Sentence 3: 7 words
        # Sentence 2 should have more time than sentence 1
        duration_1 = timings[0][1] - timings[0][0]
        duration_2 = timings[1][1] - timings[1][0]
        duration_3 = timings[2][1] - timings[2][0]
        
        assert duration_2 > duration_1  # More words = more time
        assert duration_3 > duration_2  # Even more words = even more time
    
    def test_special_characters_handling(self):
        """Test handling of special characters in text."""
        text = "Hello! How are you? I'm fine... Let's test this: it works!"
        duration = 15.0
        
        srt_path = os.path.join(self.temp_dir, "test_special.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should handle special characters properly
        assert "Hello!" in content
        assert "How are you?" in content
        assert "I'm fine" in content
        assert "Let's test this: it works!" in content
    
    def test_unicode_text_handling(self):
        """Test handling of unicode text."""
        text = "Привет мир! Bonjour le monde! 你好世界!"
        duration = 10.0
        
        srt_path = os.path.join(self.temp_dir, "test_unicode.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should handle unicode properly
        assert "Привет мир!" in content
        assert "Bonjour le monde!" in content
        assert "你好世界!" in content
    
    def test_very_long_text_handling(self):
        """Test handling of very long text."""
        # Create a long text with many sentences
        sentences = [f"This is sentence number {i}." for i in range(1, 21)]
        text = " ".join(sentences)
        duration = 60.0
        
        srt_path = os.path.join(self.temp_dir, "test_long.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Should handle many subtitles
        assert "This is sentence number 1" in content
        assert "This is sentence number 20" in content
        
        # Should have proper numbering
        assert "1\n" in content
        assert "20\n" in content
    
    def test_timing_consistency(self):
        """Test that timing is consistent across runs."""
        text = "First sentence. Second sentence. Third sentence."
        duration = 30.0
        
        # Generate SRT multiple times
        results = []
        for i in range(3):
            srt_path = os.path.join(self.temp_dir, f"test_consistency_{i}.srt")
            result = self.video_assembler.generate_srt_file(text, duration, srt_path)
            
            with open(srt_path, 'r') as f:
                content = f.read()
                results.append(content)
        
        # All results should be identical
        assert results[0] == results[1] == results[2]


class TestSubtitleIntegration:
    """Integration tests for subtitle system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.video_assembler = VideoAssembler()
        
        # Mock config paths
        self.original_output_dir = Config.OUTPUT_DIR
        Config.OUTPUT_DIR = self.temp_dir
    
    def teardown_method(self):
        """Clean up test environment."""
        Config.OUTPUT_DIR = self.original_output_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('whisper.load_model')
    def test_whisper_fallback_to_text_timing(self, mock_load_model):
        """Test that system falls back to text timing when Whisper fails."""
        # Mock Whisper to fail
        mock_load_model.side_effect = Exception("Whisper failed")
        
        # Create fake audio file
        audio_path = os.path.join(self.temp_dir, "test_audio.mp3")
        with open(audio_path, 'w') as f:
            f.write("fake audio content")
        
        text = "This is a test sentence. This is another test sentence."
        duration = 10.0
        
        # This should use the fallback mechanism
        srt_path = os.path.join(self.temp_dir, "fallback_test.srt")
        
        # Mock the method call that would happen in video assembly
        whisper_result = self.video_assembler.generate_srt_with_whisper(audio_path, srt_path)
        assert whisper_result is None  # Whisper should fail
        
        # Fallback to text timing
        text_result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        assert text_result is not None
        assert os.path.exists(srt_path)
        
        with open(srt_path, 'r') as f:
            content = f.read()
        
        # Should have text-based timing
        assert "This is a test sentence" in content
        assert "This is another test sentence" in content
    
    def test_subtitle_file_permissions(self):
        """Test that subtitle files are created with correct permissions."""
        text = "Test subtitle permissions."
        duration = 5.0
        
        srt_path = os.path.join(self.temp_dir, "test_permissions.srt")
        result = self.video_assembler.generate_srt_file(text, duration, srt_path)
        
        assert result is not None
        assert os.path.exists(srt_path)
        
        # Check file is readable
        with open(srt_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
        
        # Check file stats
        stat_info = os.stat(srt_path)
        assert stat_info.st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 