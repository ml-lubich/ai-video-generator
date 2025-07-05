#!/usr/bin/env python3
"""
Setup script for AI Video Generator.
Automatically configures API keys and validates system setup.
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the environment configuration."""
    print("🎬 AI Video Generator Setup")
    print("=" * 40)
    
    # Get API key from user
    api_key = input("\n📝 Enter your Pexels API key: ").strip()
    
    if not api_key:
        print("❌ API key is required. Get one free at: https://www.pexels.com/api/")
        return False
    
    # Create .env file
    env_content = f"""# AI Video Generator Configuration
PEXELS_API_KEY={api_key}

# Optional voice settings (uncomment to customize)
# DEFAULT_VOICE=en-US-AriaNeural
# VOICE_SPEED=+0%
# VOICE_PITCH=+0Hz

# Optional video settings (uncomment to customize)
# DEFAULT_FPS=24
# DEFAULT_DURATION=5
# DEFAULT_RESOLUTION_WIDTH=1920
# DEFAULT_RESOLUTION_HEIGHT=1080
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Configuration saved to .env file")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def validate_setup():
    """Validate that the setup is working."""
    print("\n🔍 Validating setup...")
    
    try:
        # Test imports
        import edge_tts
        import moviepy
        import requests
        from PIL import Image
        print("✅ All required modules available")
        
        # Test config loading
        from config import Config
        Config.ensure_directories()
        print("✅ Configuration loaded")
        
        # Test API key
        if Config.get_pexels_api_key():
            print("✅ Pexels API key configured")
        else:
            print("❌ Pexels API key not found")
            return False
        
        # Test voice generation
        try:
            from voice_generator import VoiceGenerator
            print("✅ Voice generation module ready")
        except Exception as e:
            print(f"❌ Voice generation test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup validation failed: {e}")
        return False

def run_demo():
    """Run a quick demo to verify everything works."""
    print("\n🚀 Running quick demo...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'main.py', 'run-pipeline', 
            '--pipeline', 'quick-demo'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Demo completed successfully!")
            print("📹 Check the output/ directory for your generated video")
            return True
        else:
            print(f"❌ Demo failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Demo taking longer than expected (this is normal for first run)")
        return True
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

def main():
    """Main setup function."""
    print("🎬 Welcome to AI Video Generator Setup!")
    print("\nThis script will:")
    print("1. Configure your Pexels API key")
    print("2. Install required dependencies") 
    print("3. Validate the setup")
    print("4. Run a quick demo")
    
    proceed = input("\n👍 Continue? (y/N): ").lower().strip()
    if proceed != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Environment setup
    if not setup_environment():
        print("❌ Setup failed at environment configuration")
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Step 3: Validate setup
    if not validate_setup():
        print("❌ Setup validation failed")
        return
    
    # Step 4: Optional demo
    run_demo_choice = input("\n🎯 Run demo video generation? (y/N): ").lower().strip()
    if run_demo_choice == 'y':
        run_demo()
    
    print("\n🎉 Setup Complete!")
    print("\n📖 Quick Start:")
    print("   python main.py list-pipelines")
    print("   python main.py run-pipeline --pipeline quick-demo")
    print("   python main.py run-pipeline --pipeline nature-documentary")
    print("\n💡 Pro tip: Check out QUICKSTART.md for more examples!")

if __name__ == "__main__":
    main() 