# AI Video Generator

A comprehensive, modular AI video generation system that creates professional videos with AI-generated voices and real stock footage. Built with Python following SOLID principles for maintainability and extensibility.

## 🎬 Features

- **AI Voice Generation**: Natural-sounding speech using Microsoft Edge TTS with 17 available voices
- **Real Stock Footage**: Automatic fetching of high-quality images and videos from Pexels API
- **Professional Video Assembly**: Sophisticated video composition with MoviePy
- **Pre-configured Pipelines**: 11 ready-to-use video templates across different topics
- **Modular Architecture**: Clean separation of concerns with 7 specialized components
- **Flexible CLI**: Comprehensive command-line interface with voice selection and customization
- **Subtitle Support**: Optional text overlays for accessibility
- **Custom Parameters**: Full control over video generation parameters

## 🏗️ Project Structure

```
video-generator/
├── src/                    # Source code modules
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management
│   ├── voice_generator.py  # AI voice synthesis
│   ├── asset_fetcher.py    # Pexels API integration
│   ├── video_assembler.py  # Video composition
│   ├── pipeline_config.py  # Pipeline definitions
│   └── pipeline_runner.py  # Pipeline execution
├── docs/                   # Documentation
│   ├── README.md          # This file
│   └── QUICKSTART.md      # Quick start guide
├── assets/                 # Downloaded media files
│   ├── audio/             # Generated voice files
│   ├── images/            # Downloaded images
│   └── clips/             # Downloaded video clips
├── output/                 # Generated videos (gitignored)
├── main.py                 # CLI entry point
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
└── .gitignore            # Git ignore rules
```

## 🚀 Quick Start

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd video-generator
python setup.py
```

2. **Configure API Key**:
```bash
# Add your Pexels API key to .env
echo "PEXELS_API_KEY=your_api_key_here" > .env
```

3. **Generate Your First Video**:
```bash
python main.py run-pipeline --pipeline quick-demo
```

## 📋 Available Pipelines

### Nature & Travel
- `nature-documentary` - Wildlife and nature exploration
- `ocean-exploration` - Marine life and underwater scenes
- `mountain-expedition` - Mountain landscapes and adventures
- `travel-adventure` - Travel destinations and experiences

### Business & Technology
- `business-success` - Entrepreneurship and business growth
- `startup-journey` - Startup stories and innovation
- `tech-innovation` - Technology trends and innovations
- `ai-future` - Artificial intelligence and future tech

### Lifestyle & Health
- `culinary-journey` - Food and cooking experiences
- `wellness-lifestyle` - Health and wellness content

### Demo
- `quick-demo` - Fast test video for system verification

## 🎤 Voice Options

### Male Voices (9 available)
- `en-US-BrianNeural` ⭐ (Default - Deep, professional)
- `en-US-AndrewNeural` - Warm, friendly
- `en-US-GuyNeural` - Confident, clear
- `en-US-DavisNeural` - Authoritative
- `en-US-JasonNeural` - Energetic
- `en-US-RogerNeural` - Mature
- `en-US-SteffanNeural` - Smooth
- `en-US-TonyNeural` - Casual
- `en-US-RyanNeural` - Young, dynamic

### Female Voices (8 available)
- `en-US-AriaNeural` - Professional, clear
- `en-US-JennyNeural` - Friendly, warm
- `en-US-AvaNeural` - Sophisticated
- `en-US-EmmaNeural` - Cheerful
- `en-US-MichelleNeural` - Confident
- `en-US-NancyNeural` - Mature
- `en-US-AmberNeural` - Energetic
- `en-US-AshleyNeural` - Young, vibrant

## 🔧 Usage Examples

### Basic Pipeline Execution
```bash
python main.py run-pipeline --pipeline nature-documentary
```

### Custom Text Override
```bash
python main.py run-pipeline --pipeline tech-innovation --text "Exploring the future of quantum computing and its revolutionary applications in solving complex problems."
```

### Voice Customization
```bash
# Use specific voice
python main.py run-pipeline --pipeline business-success --voice en-US-BrianNeural

# Random voice selection
python main.py run-pipeline --pipeline travel-adventure --randomize-voice

# Gender preference
python main.py run-pipeline --pipeline culinary-journey --voice-gender female
```

### Subtitle Support
```bash
# Add subtitles with spoken text
python main.py run-pipeline --pipeline wellness-lifestyle --subtitles

# Custom subtitle text
python main.py run-pipeline --pipeline startup-journey --subtitles --subtitle-text "The Journey to Success"
```

### Custom Video Creation
```bash
python main.py create-custom \
  --text "Your custom narration text here" \
  --search "sunset ocean waves" \
  --voice en-US-AriaNeural \
  --images 5 \
  --videos 2 \
  --output my-custom-video \
  --subtitles
```

## 📊 System Commands

### List Available Options
```bash
python main.py list-pipelines    # Show all video templates
python main.py list-voices       # Show all available voices
python main.py check-status      # Verify system configuration
```

### System Status Check
```bash
python main.py check-status
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
PEXELS_API_KEY=your_pexels_api_key_here
```

### Key Configuration Options
- **Voice Selection**: 17 Microsoft Neural voices with gender grouping
- **Asset Limits**: Configurable image/video counts per pipeline
- **Output Quality**: 720p HD video output with AAC audio
- **Subtitle Styling**: Customizable text overlays with professional styling

## 🧩 Architecture

### Core Components

1. **Config** (`src/config.py`): Centralized configuration management
2. **VoiceGenerator** (`src/voice_generator.py`): AI voice synthesis with edge-tts
3. **AssetFetcher** (`src/asset_fetcher.py`): Pexels API integration
4. **VideoAssembler** (`src/video_assembler.py`): MoviePy-based video composition
5. **PipelineConfig** (`src/pipeline_config.py`): Pipeline definitions and management
6. **PipelineRunner** (`src/pipeline_runner.py`): Orchestrates complete video generation

### Design Principles
- **Single Responsibility**: Each module has one clear purpose
- **Separation of Concerns**: Clear boundaries between components
- **Composition over Inheritance**: Flexible component interaction
- **DRY**: Shared utilities and configurations
- **KISS**: Simple, maintainable implementations

## 📦 Dependencies

- `edge-tts` - Microsoft Edge Text-to-Speech
- `moviepy` - Video editing and composition
- `requests` - HTTP client for API calls
- `Pillow` - Image processing
- `python-dotenv` - Environment variable management
- `click` - Command-line interface framework

## 🔍 Troubleshooting

### Common Issues

1. **No Audio in Videos**:
   - Verify edge-tts is installed: `pip install edge-tts`
   - Check audio file generation in `assets/audio/`

2. **Asset Download Failures**:
   - Verify Pexels API key in `.env` file
   - Check internet connectivity
   - Confirm API key permissions

3. **Video Assembly Errors**:
   - Ensure MoviePy is properly installed
   - Check available disk space
   - Verify asset file integrity

### Performance Tips
- Use fewer images/videos for faster generation
- Clean `assets/` directory periodically
- Monitor system resources during generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style and architecture
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, feature requests, or questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Made with ❤️ by the Video Generator Team** 