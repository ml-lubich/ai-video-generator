# 🎬 Unified Video Creator - Usage Guide

**Single entry point for creating videos with custom text OR AI-generated content**

## 🚀 **Quick Start**

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set up API Key (Required)
```bash
# Create .env file
echo "PEXELS_API_KEY=your_pexels_api_key_here" > .env
```

### Basic Usage
```bash
# Custom text video (no AI required)
python main.py --text "Hello world! This is my first video."

# AI-generated video (requires Ollama)
python main.py --category technology --length 90
```

## 📝 **Custom Text Videos**

Create videos with your own script:

```bash
# Simple custom video
python main.py --text "Welcome to my channel!"

# Custom video with category for better assets
python main.py \
  --text "Today we're exploring the wonders of space travel" \
  --category science \
  --length 120

# Multi-language custom video
python main.py \
  --text "Bonjour! Bienvenue sur ma chaîne YouTube" \
  --language fr-FR \
  --voice-gender male

# Custom video with specific settings
python main.py \
  --text "This is a detailed tutorial about machine learning" \
  --category technology \
  --output "ml_tutorial" \
  --subtitles \
  --subtitle-style modern \
  --images 6 \
  --videos 3
```

## 🤖 **AI-Generated Videos**

Let AI create content for you:

```bash
# Set up Ollama first (one time setup)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3.2

# Generate AI video with category
python main.py --category technology --length 120

# Generate random AI video
python main.py --length 60

# AI video with specific settings
python main.py \
  --category science \
  --length 180 \
  --language en-US \
  --voice-gender female \
  --subtitle-style cinematic \
  --output "ai_science_video"
```

## 🎯 **All Available Options**

```bash
python main.py [OPTIONS]

# Content Options
--text "Your script here"           # Custom text (if not provided, AI generates)
--category "technology"             # Content category (optional)
--length 120                        # Average length in seconds (guides AI)

# Language & Voice
--language en-US                    # Language (default: en-US)
--voice-gender male                 # Voice preference: male/female/random

# Output Options  
--output "my_video"                 # Output filename (without extension)
--subtitles / --no-subtitles        # Enable/disable subtitles (default: enabled)
--subtitle-style professional      # Style: professional/modern/cinematic

# Assets
--images 4                          # Number of images (default: 4)
--videos 2                          # Number of video clips (default: 2)

# Upload
--upload / --no-upload              # Upload to YouTube (default: no)

# AI Options
--ai-model llama3.2                 # AI model for content generation

# Debug
--verbose                           # Enable verbose logging
```

## 🌍 **Supported Languages**

```bash
# List all supported languages
python main.py list-languages

# Examples for different languages
python main.py --text "Привет мир!" --language ru-RU
python main.py --text "Hola mundo!" --language es-ES  
python main.py --text "Bonjour le monde!" --language fr-FR
python main.py --text "Hallo Welt!" --language de-DE
```

## 📊 **Subtitle Styles**

### Professional (Default)
- Clean, readable font
- High contrast
- Business/educational content

```bash
python main.py --text "Professional presentation" --subtitle-style professional
```

### Modern
- Stylish, contemporary look
- Subtle styling
- Social media content

```bash
python main.py --text "Modern social content" --subtitle-style modern
```

### Cinematic
- Dramatic, movie-like appearance
- Gold text with shadows
- Entertainment content

```bash
python main.py --text "Epic movie trailer style" --subtitle-style cinematic
```

## 🧪 **Testing the System**

```bash
# Run all tests
python run_tests.py

# Quick functional test
python run_tests.py --quick

# Verbose test output
python run_tests.py --verbose

# Test system components
python main.py test-systems
```

## 📺 **YouTube Upload Setup**

1. **Get YouTube API Credentials**:
   - Go to [Google Cloud Console](https://console.developers.google.com/)
   - Create project and enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download as `youtube_credentials.json`

2. **Upload Videos**:
```bash
# Upload custom video
python main.py \
  --text "My awesome video content" \
  --upload

# Upload AI-generated video
python main.py \
  --category technology \
  --length 180 \
  --upload
```

## ⚡ **Performance Tips**

### Fast Generation
```bash
# Minimal assets for speed
python main.py \
  --text "Quick test video" \
  --images 2 \
  --videos 1 \
  --length 30
```

### High Quality
```bash
# More assets for better quality
python main.py \
  --text "High quality production" \
  --images 8 \
  --videos 4 \
  --length 180 \
  --subtitles \
  --subtitle-style cinematic
```

## 🔧 **Troubleshooting**

### Common Issues

**"AI system not available"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Install model
ollama pull llama3.2
```

**"No API key found"**
```bash
# Set Pexels API key
echo "PEXELS_API_KEY=your_key_here" > .env
```

**"Module not found"**
```bash
# Install dependencies
pip install -r requirements.txt
```

**"Permission denied"**
```bash
# Make script executable
chmod +x main.py
```

## 📈 **Examples by Use Case**

### Content Creator
```bash
# Daily short video
python main.py \
  --category entertainment \
  --length 60 \
  --voice-gender female \
  --subtitle-style modern

# Weekly deep dive
python main.py \
  --category education \
  --length 600 \
  --subtitles \
  --images 10 \
  --videos 5
```

### Business
```bash
# Product demo
python main.py \
  --text "Introducing our revolutionary new product that will change everything" \
  --category business \
  --subtitle-style professional \
  --upload

# Training video
python main.py \
  --text "Welcome to employee training module 1: Company policies and procedures" \
  --category education \
  --length 300
```

### Educational Content
```bash
# Science explainer
python main.py \
  --category science \
  --length 240 \
  --subtitle-style professional \
  --images 8

# Language learning
python main.py \
  --text "Learn basic French phrases: Bonjour, comment allez-vous?" \
  --language fr-FR \
  --category education
```

## 🎯 **Pro Tips**

1. **Use categories** for better asset matching
2. **Set appropriate length** to guide AI content generation
3. **Enable subtitles** for better accessibility
4. **Test with short videos** first to verify setup
5. **Use verbose mode** for debugging issues

## 🔄 **Workflow Examples**

### Daily Content Creation
```bash
# Generate 5 videos for the week
for category in technology science health business education; do
  python main.py --category $category --length 90 --upload
done
```

### A/B Testing Content
```bash
# Version A: Professional style
python main.py --text "Product launch announcement" --subtitle-style professional --output "version_a"

# Version B: Modern style  
python main.py --text "Product launch announcement" --subtitle-style modern --output "version_b"
```

### Multi-language Content
```bash
# English version
python main.py --text "Welcome to our channel" --language en-US --output "welcome_en"

# Spanish version
python main.py --text "Bienvenidos a nuestro canal" --language es-ES --output "welcome_es"

# French version
python main.py --text "Bienvenue sur notre chaîne" --language fr-FR --output "welcome_fr"
```

---

**For more advanced usage, see the full README.md documentation.** 