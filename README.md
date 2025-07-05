# 🎬 AI Video Factory

**Complete AI-powered video generation and publishing system** with automated content creation, subtitle synchronization, and YouTube publishing.

## 🚀 **What It Does**

- **🧠 AI Content Generation**: Uses Ollama to generate trending topics, scripts, and metadata
- **🎤 Natural Voice Synthesis**: 17 AI voices in 16 languages with edge-TTS
- **📸 Asset Fetching**: Downloads images and videos from Pexels API
- **🎥 Video Assembly**: Creates videos with MoviePy and accurate subtitle timing
- **📺 YouTube Publishing**: Automated upload with metadata and scheduling
- **🏭 Factory Mode**: Continuous production of multiple videos per day

## 🏗️ **System Architecture**

### Core Components (SOLID Principles)
- **config.py** - Centralized configuration management
- **content_generator.py** - AI content generation using Ollama
- **voice_generator.py** - AI voice synthesis (Single Responsibility)
- **asset_fetcher.py** - Pexels API integration
- **video_assembler.py** - MoviePy video composition with Whisper subtitles
- **youtube_uploader.py** - YouTube API integration
- **video_factory.py** - Master orchestrator

### Pipeline System
- **pipeline_config.py** - Pre-configured pipelines
- **pipeline_runner.py** - Pipeline execution
- **main.py** - CLI interface

## 📋 **Setup Instructions**

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Ollama (Required for AI Content Generation)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull AI model (in another terminal)
ollama pull llama3.2
```

### 3. Configure API Keys
Create `.env` file:
```bash
# Pexels API (required for images/videos)
PEXELS_API_KEY=your_pexels_api_key_here

# YouTube API (optional - for publishing)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 4. Set up YouTube API (Optional)
For automated YouTube publishing:

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials**
5. Download credentials as `youtube_credentials.json`
6. Place in project root directory

## 🎯 **Usage**

### Basic Video Generation
```bash
# Generate single video with AI content
python -m src.video_factory generate --category technology --duration 60

# Generate batch of videos
python -m src.video_factory batch --count 5 --duration 60

# Test all systems
python -m src.video_factory setup
```

### Manual Video Creation
```bash
# Create video with custom text
python main.py create-custom \
  --text "Your video script here" \
  --search "relevant keywords" \
  --output my_video \
  --subtitles

# Use pre-configured pipeline
python main.py run-pipeline nature-documentary
```

### Advanced Features
```bash
# Multi-language support
python main.py create-custom \
  --text "Привет! Это тест русского голоса." \
  --language ru-RU \
  --voice-gender male \
  --subtitles

# Continuous production (10 videos/day)
python -m src.video_factory continuous --videos-per-day 10 --upload
```

## 🎤 **Voice System**

### Supported Languages (16 total)
- **English**: `en-US-BrianNeural` (default male)
- **Russian**: `ru-RU-DmitryNeural`
- **Spanish**: `es-ES-AlvaroNeural`
- **French**: `fr-FR-HenriNeural`
- **German**: `de-DE-ConradNeural`
- **And 11 more languages...

### Voice Selection
```bash
# List all available voices
python main.py list-voices

# Use specific voice
python main.py create-custom --voice en-US-BrianNeural

# Random voice selection
python main.py create-custom --randomize-voice

# Gender preference
python main.py create-custom --voice-gender male
```

## 📊 **Subtitle System**

### Accurate Timing with Whisper
- **Text-based timing**: Proportional to sentence length
- **Whisper timing**: AI-analyzed speech patterns for perfect sync
- **Three styles**: Professional, Modern, Cinematic

### Subtitle Styles
```bash
# Professional style (default)
python main.py create-custom --subtitle-style professional

# Modern style
python main.py create-custom --subtitle-style modern

# Cinematic style
python main.py create-custom --subtitle-style cinematic
```

## 🏭 **AI Video Factory**

### Automated Production
```python
from src.video_factory import VideoFactory

factory = VideoFactory()

# Set up systems
factory.setup_systems()

# Generate single video
result = factory.generate_single_video(
    category="technology",
    duration=60,
    upload=False
)

# Batch generation
results = factory.generate_batch_videos(
    count=10,
    duration=60,
    upload=True
)

# Continuous production
factory.run_continuous_production(
    videos_per_day=10,
    upload=True
)
```

### Factory Configuration
```python
factory.configure_settings(
    default_duration=90,
    upload_to_youtube=True,
    auto_publish=True,
    preferred_categories=["technology", "science", "education"]
)
```

## 📺 **YouTube Integration**

### Upload Features
- **Automated upload** with metadata
- **Custom thumbnails**
- **Scheduled publishing**
- **Privacy controls** (public/unlisted/private)
- **Category selection**

### Upload Example
```python
from src.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
uploader.setup_authentication()

video_id = uploader.upload_video(
    video_path="output/my_video.mp4",
    title="My AI Generated Video",
    description="Created with AI Video Factory",
    tags=["ai", "automation", "video"],
    privacy_status="public"
)
```

## 🔧 **Configuration**

### Pipeline Configuration
```python
# src/pipeline_config.py
PIPELINE_CONFIGS = {
    "tech-innovation": PipelineConfig(
        name="tech-innovation",
        description="Technology innovation content",
        script_template="Explore the latest in {topic}...",
        search_terms=["technology", "innovation", "digital"],
        voice_gender="male",
        subtitle_style="professional"
    )
}
```

### Asset Configuration
```python
# src/config.py
class Config:
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    MAX_IMAGES = 10
    MAX_VIDEOS = 5
    DEFAULT_VOICE = "en-US-BrianNeural"
    OUTPUT_DIR = "output"
```

## 📈 **Performance**

### Generation Times
- **Single video**: ~60-90 seconds
- **Batch (5 videos)**: ~5-7 minutes
- **AI content generation**: ~10-15 seconds
- **Voice synthesis**: ~5-10 seconds
- **Video assembly**: ~30-60 seconds

### Resource Usage
- **Memory**: 2-4 GB during generation
- **Storage**: ~1-5 MB per video
- **Network**: Depends on asset downloads

## 🛠️ **Troubleshooting**

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model
ollama pull llama3.2
```

**YouTube Authentication Failed**
1. Check `youtube_credentials.json` exists
2. Verify YouTube Data API v3 is enabled
3. Ensure OAuth consent screen is configured

**Subtitle Timing Issues**
- Whisper provides most accurate timing
- Falls back to text-based timing if Whisper fails
- Check audio file quality for best results

**Missing Dependencies**
```bash
# Install missing packages
pip install openai-whisper google-auth google-auth-oauthlib

# For macOS users
brew install ffmpeg
```

## 🎯 **Use Cases**

### Content Creators
- **Daily content**: Generate videos for YouTube, TikTok, Instagram
- **Multi-language**: Create content in 16 languages
- **Batch production**: Generate weeks of content at once

### Businesses
- **Product demos**: Automated product showcase videos
- **Educational content**: Training and explanation videos
- **Marketing**: Social media content at scale

### Developers
- **API integration**: Extend with custom APIs
- **Custom pipelines**: Create specialized content types
- **Automation**: Integrate with CI/CD or cron jobs

## 📚 **API Reference**

### VideoFactory Class
```python
class VideoFactory:
    def __init__(self, ollama_host: str, model: str)
    def setup_systems(self) -> bool
    def generate_single_video(self, **kwargs) -> Dict
    def generate_batch_videos(self, **kwargs) -> List[Dict]
    def run_continuous_production(self, **kwargs)
    def print_stats(self)
```

### Content Generator
```python
class OllamaContentGenerator:
    def generate_topic(self, category: str) -> str
    def generate_script(self, topic: str, duration: int) -> str
    def generate_complete_content(self, **kwargs) -> VideoContent
```

## 🤝 **Contributing**

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd video-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Code Style
- Follow **SOLID principles**
- Use **type hints**
- Add **comprehensive logging**
- Write **modular components**

## 📄 **License**

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 **Acknowledgments**

- **OpenAI Whisper** for speech recognition
- **Edge TTS** for voice synthesis
- **MoviePy** for video processing
- **Pexels** for stock media
- **Ollama** for AI content generation

---

**Built with ❤️ using SOLID principles and modern Python practices**

For questions or issues, please create an issue in the repository. 