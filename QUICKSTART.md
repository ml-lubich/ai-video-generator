# 🎬 AI Video Generator - Quick Start

Generate professional videos from text in **3 simple steps**!

## ⚡ Instant Setup

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set your Pexels API key (get free at https://www.pexels.com/api/)
export PEXELS_API_KEY="your_api_key_here"

# 3. Generate your first video!
python main.py run-pipeline --pipeline "quick-demo"
```

## 🎯 One-Command Video Generation

### Pre-configured Pipelines (Ready to Use!)

```bash
# Nature Documentary
python main.py run-pipeline --pipeline "nature-documentary"

# Tech Innovation 
python main.py run-pipeline --pipeline "tech-innovation"

# Business Success
python main.py run-pipeline --pipeline "business-success"

# Travel Adventure
python main.py run-pipeline --pipeline "travel-adventure"

# Ocean Exploration
python main.py run-pipeline --pipeline "ocean-exploration"
```

### Custom Text + Any Pipeline

```bash
python main.py run-pipeline \
  --pipeline "nature-documentary" \
  --text "Your custom narration goes here"
```

## 🔧 Available Commands

```bash
# List all pipelines
python main.py list-pipelines

# Check system status
python main.py status

# Create custom pipeline
python main.py create-pipeline \
  --name "my-video" \
  --text "Amazing content" \
  --query "search terms" \
  --run
```

## 📁 What You Get

- 🎤 **AI Voice:** Natural Microsoft Neural voices
- 🖼️ **Images:** High-quality stock photos from Pexels
- 🎥 **Videos:** Professional stock footage from Pexels
- 📹 **Output:** Ready-to-use MP4 videos

## 💡 Tips

- Videos are saved to `output/` directory
- Use `--text` to customize narration
- 17 different AI voices available
- All pipelines work out of the box
- No configuration files needed!

---

**That's it! Start creating videos now! 🚀** 