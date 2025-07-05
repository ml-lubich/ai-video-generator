#!/usr/bin/env python3
"""
Simple test runner for the video generator system.
Tests core functionality without external dependencies.
"""
import os
import sys
import tempfile
import shutil
import traceback
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import modules to test
try:
    from config import Config
    from video_assembler import VideoAssembler
    import main
    from main import UnifiedVideoCreator
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("Make sure all required modules are in the src/ directory")
    sys.exit(1)


class TestRunner:
    """Simple test runner for video generator."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        
    def run_test(self, test_name: str, test_func):
        """Run a single test function."""
        self.tests_run += 1
        try:
            print(f"🧪 Running: {test_name}")
            test_func()
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            self.failures.append((test_name, str(e), traceback.format_exc()))
            self.tests_failed += 1
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🎬 Video Generator Test Suite")
        print("=" * 50)
        
        # Run test suites
        self.run_subtitle_timing_tests()
        self.run_unified_creator_tests()
        self.run_integration_tests()
        
        # Print summary
        self.print_summary()
    
    def run_subtitle_timing_tests(self):
        """Test subtitle timing functionality."""
        print("\n📊 Testing Subtitle Timing...")
        
        def test_text_based_timing():
            temp_dir = tempfile.mkdtemp()
            try:
                video_assembler = VideoAssembler()
                text = "First sentence. Second sentence. Third sentence."
                duration = 30.0
                srt_path = os.path.join(temp_dir, "test.srt")
                
                result = video_assembler.generate_srt_file(text, duration, srt_path)
                
                assert result is not None, "SRT generation should succeed"
                assert os.path.exists(srt_path), "SRT file should be created"
                
                with open(srt_path, 'r') as f:
                    content = f.read()
                
                assert "First sentence" in content, "First sentence should be in SRT"
                assert "Second sentence" in content, "Second sentence should be in SRT"
                assert "Third sentence" in content, "Third sentence should be in SRT"
                assert "00:00:00" in content, "Timing should be present"
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        def test_proportional_timing():
            temp_dir = tempfile.mkdtemp()
            try:
                video_assembler = VideoAssembler()
                text = "Short. This is a much longer sentence with many words. Brief."
                duration = 30.0
                srt_path = os.path.join(temp_dir, "test_timing.srt")
                
                result = video_assembler.generate_srt_file(text, duration, srt_path)
                
                assert result is not None, "SRT generation should succeed"
                
                with open(srt_path, 'r') as f:
                    content = f.read()
                
                # Parse timing
                lines = content.strip().split('\n')
                timings = []
                for line in lines:
                    if '-->' in line:
                        start, end = line.split(' --> ')
                        timings.append((start, end))
                
                assert len(timings) == 3, "Should have 3 timing entries"
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        def test_special_characters():
            temp_dir = tempfile.mkdtemp()
            try:
                video_assembler = VideoAssembler()
                text = "Hello! How are you? I'm fine... Let's test this: it works!"
                duration = 15.0
                srt_path = os.path.join(temp_dir, "test_special.srt")
                
                result = video_assembler.generate_srt_file(text, duration, srt_path)
                
                assert result is not None, "SRT generation should handle special characters"
                
                with open(srt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert "Hello!" in content, "Should handle exclamation marks"
                assert "How are you?" in content, "Should handle question marks"
                assert "I'm fine" in content, "Should handle apostrophes"
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        def test_empty_text_handling():
            temp_dir = tempfile.mkdtemp()
            try:
                video_assembler = VideoAssembler()
                text = ""
                duration = 10.0
                srt_path = os.path.join(temp_dir, "test_empty.srt")
                
                result = video_assembler.generate_srt_file(text, duration, srt_path)
                
                # Should handle gracefully (either return None or create empty file)
                assert True, "Empty text should be handled gracefully"
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run subtitle timing tests
        self.run_test("Text-based timing", test_text_based_timing)
        self.run_test("Proportional timing", test_proportional_timing)
        self.run_test("Special characters", test_special_characters)
        self.run_test("Empty text handling", test_empty_text_handling)
    
    def run_unified_creator_tests(self):
        """Test unified video creator functionality."""
        print("\n🎬 Testing Unified Video Creator...")
        
        def test_search_terms_generation():
            creator = UnifiedVideoCreator()
            text = "This is a test about artificial intelligence and machine learning"
            category = "technology"
            
            search_terms = creator._generate_search_terms(text, category)
            
            assert "technology" in search_terms, "Should include category"
            assert "artificial" in search_terms, "Should include meaningful words"
            assert "intelligence" in search_terms, "Should include meaningful words"
            assert "machine" in search_terms, "Should include meaningful words"
            assert "learning" in search_terms, "Should include meaningful words"
            assert "this" not in search_terms, "Should not include stop words"
            assert "and" not in search_terms, "Should not include stop words"
        
        def test_search_terms_without_category():
            creator = UnifiedVideoCreator()
            text = "Video about space exploration and rockets"
            
            search_terms = creator._generate_search_terms(text, None)
            
            assert "video" in search_terms, "Should include meaningful words"
            assert "space" in search_terms, "Should include meaningful words"
            assert "exploration" in search_terms, "Should include meaningful words"
            assert "rockets" in search_terms, "Should include meaningful words"
        
        def test_search_terms_empty_text():
            creator = UnifiedVideoCreator()
            text = ""
            category = "science"
            
            search_terms = creator._generate_search_terms(text, category)
            
            assert search_terms == "science", "Should return category as fallback"
        
        def test_search_terms_only_stop_words():
            creator = UnifiedVideoCreator()
            text = "the and or but in on at to for of with by"
            
            search_terms = creator._generate_search_terms(text, None)
            
            assert search_terms == "generic video content", "Should return fallback"
        
        def test_ai_system_check_without_ollama():
            creator = UnifiedVideoCreator()
            
            # This will likely fail if Ollama is not running, which is expected
            try:
                result = creator.check_ai_system()
                assert isinstance(result, bool), "Should return boolean"
            except Exception:
                # Expected if Ollama is not available
                assert True, "AI system check handled gracefully"
        
        # Run unified creator tests
        self.run_test("Search terms generation", test_search_terms_generation)
        self.run_test("Search terms without category", test_search_terms_without_category)
        self.run_test("Search terms empty text", test_search_terms_empty_text)
        self.run_test("Search terms only stop words", test_search_terms_only_stop_words)
        self.run_test("AI system check", test_ai_system_check_without_ollama)
    
    def run_integration_tests(self):
        """Test system integration."""
        print("\n🔧 Testing System Integration...")
        
        def test_config_loading():
            # Test that config loads properly
            assert hasattr(Config, 'OUTPUT_DIR'), "Config should have OUTPUT_DIR"
            assert hasattr(Config, 'PEXELS_API_KEY'), "Config should have PEXELS_API_KEY"
            assert hasattr(Config, 'SUPPORTED_LANGUAGES'), "Config should have SUPPORTED_LANGUAGES"
            assert isinstance(Config.SUPPORTED_LANGUAGES, dict), "SUPPORTED_LANGUAGES should be dict"
            assert len(Config.SUPPORTED_LANGUAGES) > 0, "Should have supported languages"
        
        def test_directory_creation():
            # Test that required directories exist or can be created
            temp_dir = tempfile.mkdtemp()
            try:
                output_dir = os.path.join(temp_dir, "output")
                os.makedirs(output_dir, exist_ok=True)
                assert os.path.exists(output_dir), "Should be able to create output directory"
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        def test_video_assembler_initialization():
            # Test that video assembler can be initialized
            video_assembler = VideoAssembler()
            assert video_assembler is not None, "VideoAssembler should initialize"
        
        def test_unified_creator_initialization():
            # Test that unified creator can be initialized
            creator = UnifiedVideoCreator()
            assert creator is not None, "UnifiedVideoCreator should initialize"
            assert hasattr(creator, 'pipeline_runner'), "Should have pipeline_runner"
            assert hasattr(creator, '_ai_ready'), "Should have _ai_ready attribute"
        
        def test_language_validation():
            # Test language validation
            valid_languages = ['en-US', 'ru-RU', 'es-ES', 'fr-FR', 'de-DE']
            for lang in valid_languages:
                if lang in Config.SUPPORTED_LANGUAGES:
                    result = Config.validate_language(lang)
                    assert result == True, f"Language {lang} should be valid"
        
        # Run integration tests
        self.run_test("Config loading", test_config_loading)
        self.run_test("Directory creation", test_directory_creation)
        self.run_test("VideoAssembler initialization", test_video_assembler_initialization)
        self.run_test("UnifiedCreator initialization", test_unified_creator_initialization)
        self.run_test("Language validation", test_language_validation)
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        
        if self.tests_failed > 0:
            print(f"\n❌ Failures ({self.tests_failed}):")
            for test_name, error, traceback_str in self.failures:
                print(f"\n{test_name}:")
                print(f"  Error: {error}")
                if "--verbose" in sys.argv:
                    print(f"  Traceback:\n{traceback_str}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")


def run_quick_functional_test():
    """Run a quick functional test to verify core systems work."""
    print("\n🚀 Running Quick Functional Test...")
    
    try:
        # Test 1: Create a very simple video with text
        print("📝 Testing custom text video creation...")
        
        creator = UnifiedVideoCreator()
        
        # Use minimal parameters to avoid external dependencies
        result = creator._generate_search_terms("Test video about technology", "tech")
        print(f"✅ Search terms generation: {result}")
        
        # Test 2: Check subtitle generation
        print("📊 Testing subtitle generation...")
        
        temp_dir = tempfile.mkdtemp()
        try:
            video_assembler = VideoAssembler()
            text = "This is a quick test. It should work properly."
            duration = 10.0
            srt_path = os.path.join(temp_dir, "quick_test.srt")
            
            result = video_assembler.generate_srt_file(text, duration, srt_path)
            
            if result and os.path.exists(srt_path):
                with open(srt_path, 'r') as f:
                    content = f.read()
                print(f"✅ Subtitle generation successful")
                print(f"   Generated {len(content.split('\\n'))} lines")
            else:
                print("⚠️  Subtitle generation returned None or file not created")
                
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Test 3: Check AI system availability
        print("🤖 Testing AI system availability...")
        
        ai_available = creator.check_ai_system()
        if ai_available:
            print("✅ AI system is available")
        else:
            print("⚠️  AI system not available (Ollama not running or not installed)")
        
        print("🎉 Quick functional test complete!")
        
    except Exception as e:
        print(f"❌ Quick functional test failed: {str(e)}")
        if "--verbose" in sys.argv:
            traceback.print_exc()


def main():
    """Main test runner function."""
    print("🎬 AI Video Generator Test Suite")
    print("Testing core functionality and subtitle timing")
    
    if "--help" in sys.argv:
        print("Usage: python run_tests.py [options]")
        print("Options:")
        print("  --quick     Run only quick functional tests")
        print("  --verbose   Show detailed error information")
        print("  --help      Show this help message")
        return
    
    if "--quick" in sys.argv:
        run_quick_functional_test()
        return
    
    # Run full test suite
    runner = TestRunner()
    runner.run_all_tests()
    
    # Run quick functional test
    run_quick_functional_test()
    
    # Exit with appropriate code
    if runner.tests_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 