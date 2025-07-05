# 🎬 AI Video Generator

Create professional videos with AI voices and real stock footage automatically. This system combines edge-tts for natural AI voices, Pexels API for high-quality stock content, and MoviePy for video assembly.

## ✨ Features

- 🎤 **17 AI Voices** - Natural-sounding Microsoft Neural voices (male/female)
- 🎭 **Voice Selection** - Choose specific voices, randomize, or select by gender
- 🖼️ **Real Stock Content** - Automatic fetching from Pexels API
- 🎥 **Professional Assembly** - MoviePy-based video composition
- 📝 **Subtitle Support** - Optional text overlays for clarity
- 🎯 **11 Pre-configured Pipelines** - Ready-to-use video themes
- 🔧 **Custom Videos** - Create videos with your own parameters
- 💯 **Completely Free** - No paid APIs required

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/video-generator.git
cd video-generator

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
# Get your free API key from https://www.pexels.com/api/
PEXELS_API_KEY=your_pexels_api_key_here
```

### 3. Run Setup

```bash
# Run the setup script
python setup.py
```

### 4. Generate Your First Video

```bash
# Quick demo
python main.py run-pipeline --pipeline "quick-demo"

# With custom text
python main.py run-pipeline --pipeline "nature-documentary" --text "Your custom narration here"

# With random voice and subtitles
python main.py run-pipeline --pipeline "tech-innovation" --randomize-voice --subtitles
```

## 🎯 Available Pipelines

| Pipeline | Description | Duration | Voice |
|----------|-------------|----------|-------|
| `quick-demo` | Technology demonstration | ~6s | Aria (Female) |
| `nature-documentary` | Nature and wildlife | ~20s | Aria (Female) |
| `ai-future` | Artificial intelligence | ~16s | Guy (Male) |
| `business-success` | Business and teamwork | ~9s | Ava (Female) |
| `tech-innovation` | Technology innovation | ~10.5s | Jenny (Female) |
| `travel-adventure` | Travel and exploration | ~15s | Emma (Female) |
| `startup-journey` | Entrepreneurship | ~14s | Andrew (Male) |
| `culinary-journey` | Food and cooking | ~14s | Jenny (Female) |
| `mountain-expedition` | Mountain adventure | ~16s | Brian (Male) |
| `ocean-exploration` | Marine life | ~13.5s | Brian (Male) |
| `wellness-lifestyle` | Health and wellness | ~12s | Aria (Female) |

## 🎤 Voice Options

### Available Voices (17 total)

**Male Voices (Low to High):**
- `en-US-BrianNeural` ⭐ (Default - Deep male)
- `en-US-AndrewNeural` (Mature male)
- `en-US-GuyNeural` (Professional male)
- `en-US-DavisNeural` (Warm male)
- `en-US-JasonNeural` (Friendly male)
- `en-US-RogerNeural` (Authoritative)
- `en-US-TonyNeural` (Confident)
- `en-US-RyanNeural` (Casual)

**Female Voices:**
- `en-US-AriaNeural` (Clear female)
- `en-US-JennyNeural` (Expressive female)
- `en-US-AvaNeural` (Conversational female)
- `en-US-EmmaNeural` (Warm female)
- `en-US-MichelleNeural` (Professional female)
- `en-US-NancyNeural` (Storytelling)
- `en-US-AmberNeural` (Friendly)
- `en-US-AshleyNeural` (Expressive)

### Voice Selection Options

```bash
# Specific voice
python main.py run-pipeline --pipeline "nature-documentary" --voice "en-US-BrianNeural"

# Random voice
python main.py run-pipeline --pipeline "tech-innovation" --randomize-voice

# Gender preference
python main.py run-pipeline --pipeline "business-success" --voice-gender "male"
python main.py run-pipeline --pipeline "travel-adventure" --voice-gender "female"
```

## 📝 CLI Commands

### Run Pipelines

```bash
# Basic pipeline
python main.py run-pipeline --pipeline "nature-documentary"

# With custom text
python main.py run-pipeline --pipeline "ai-future" --text "Your custom narration here"

# With voice options
python main.py run-pipeline --pipeline "tech-innovation" --voice "en-US-BrianNeural"
python main.py run-pipeline --pipeline "business-success" --randomize-voice
python main.py run-pipeline --pipeline "travel-adventure" --voice-gender "female"

# With subtitles
python main.py run-pipeline --pipeline "nature-documentary" --subtitles
python main.py run-pipeline --pipeline "ai-future" --subtitles --subtitle-text "Custom subtitle text"

# Custom output filename
python main.py run-pipeline --pipeline "tech-innovation" --output "my-video"
```

### Create Custom Videos

```bash
# Basic custom video
python main.py create-custom \
  --text "Your custom narration text here" \
  --search "nature landscape mountains" \
  --voice "en-US-BrianNeural"

# With all options
python main.py create-custom \
  --text "Welcome to our amazing product demo" \
  --search "technology innovation office" \
  --voice-gender "male" \
  --images 5 \
  --videos 2 \
  --output "product-demo" \
  --subtitles \
  --subtitle-text "Product Demo Video"
```

### List and Info Commands

```bash
# List all pipelines
python main.py list-pipelines

# List all voices
python main.py list-voices

# Check system status
python main.py check-status
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required: Pexels API key
PEXELS_API_KEY=your_pexels_api_key_here
```

### Default Settings

The system uses these defaults (configurable in `config.py`):

```python
# Voice Settings
DEFAULT_VOICE = "en-US-BrianNeural"  # Low male voice
VOICE_SPEED = "+0%"
VOICE_PITCH = "+0Hz"

# Video Settings
DEFAULT_FPS = 24
DEFAULT_DURATION = 5  # seconds per image
DEFAULT_RESOLUTION = (1920, 1080)

# Subtitle Settings
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT_COLOR = "white"
SUBTITLE_POSITION = ("center", "bottom")
```

## 📁 Project Structure

```
video-generator/
├── main.py              # CLI interface
├── config.py            # Configuration management
├── voice_generator.py   # AI voice synthesis
├── asset_fetcher.py     # Stock content fetching
├── video_assembler.py   # Video composition
├── pipeline_config.py   # Pipeline definitions
├── pipeline_runner.py   # Pipeline orchestration
├── setup.py             # Automated setup
├── requirements.txt     # Dependencies
├── .env                 # API keys (create this)
├── assets/              # Downloaded assets
│   ├── images/         # Stock images
│   ├── clips/          # Stock videos
│   └── audio/          # Generated voices
└── output/             # Generated videos
```

## 🛠️ Advanced Usage

### Custom Pipeline Creation

You can create custom pipelines by modifying `pipeline_config.py`:

```python
# Add your custom pipeline
{
    "name": "custom-theme",
    "description": "Your custom video theme",
    "text": "Your narration text here",
    "search_query": "your search terms",
    "voice": "en-US-BrianNeural",
    "max_images": 4,
    "max_videos": 1,
    "image_duration": 3.0,
    "output_filename": "custom_theme.mp4"
}
```

### Subtitle Customization

Modify subtitle settings in `config.py`:

```python
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT_COLOR = "white"
SUBTITLE_FONT_FAMILY = "Arial-Bold"
SUBTITLE_POSITION = ("center", "bottom")
SUBTITLE_MARGIN = 100
```

### Voice Randomization

The system supports intelligent voice selection:

```python
# Get random voice
Config.get_random_voice()

# Get voice by gender
Config.get_voice_by_gender("male")
Config.get_voice_by_gender("female")
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Check API key configuration
   python main.py check-status
   
   # Verify .env file exists and has correct key
   cat .env
   ```

2. **Dependencies Issues**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   
   # For macOS with externally managed Python
   pip install --break-system-packages -r requirements.txt
   ```

3. **Audio Issues**
   ```bash
   # Check if audio is included in videos
   # The system now uses proper audio encoding (AAC) for compatibility
   ```

4. **Permission Issues**
   ```bash
   # Make sure directories are writable
   chmod 755 assets/ output/
   ```

### Debug Mode

For detailed logging, check the console output during video generation. The system provides comprehensive status updates.

## 📈 Performance

- **Generation Time**: ~30-90 seconds per video
- **File Sizes**: 1-15 MB depending on content
- **Resolution**: 1920x1080 (HD)
- **Frame Rate**: 24 FPS
- **Audio**: AAC encoding for broad compatibility

## 🔄 Updates

### Version 1.0.0 Features

- ✅ 17 AI voices with gender selection
- ✅ Voice randomization
- ✅ Subtitle support
- ✅ Improved audio encoding
- ✅ Better error handling
- ✅ Enhanced CLI interface
- ✅ Comprehensive status checking

## 📞 Support

For issues or questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Run `python main.py check-status` to verify configuration
3. Check the console output for detailed error messages

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. Follow the Single Responsibility Principle
2. Maintain separation of concerns
3. Add proper error handling
4. Update documentation for new features

## 📄 License

MIT License - See LICENSE file for details.

---

**Made with ❤️ using Python, edge-tts, MoviePy, and Pexels API** 