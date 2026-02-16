# AI Yoga Master System

Production-ready AI-powered yoga coaching system with real-time pose detection, safety adaptation, and intelligent feedback.

## Architecture

- **Modular Design**: Clean separation between vision, core logic, and AI layers
- **Dependency Injection**: Easy to test and extend
- **Stateless**: Scalable and production-ready
- **Configurable**: Environment-based configuration

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run system:
```bash
python main.py
```

## System Components

- **Vision Layer**: MediaPipe pose detection
- **Core Engines**: Physics, rules, safety, corrections
- **AI Layer**: LLM coaching, voice feedback
- **Progress Tracking**: Session analytics

## Configuration

Edit `.env` or `config/settings.py` to customize behavior.