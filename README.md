# Video Analysis System

A Python-based video analysis system that combines audio transcription and visual analysis to provide comprehensive insights into video content.

## Features

- Video frame analysis using CLIP
- Audio transcription using Whisper
- Interactive GUI for video upload and analysis
- Progress tracking during analysis
- Save analysis results to file
- Support for multiple video formats

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd video-analysis
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the GUI application:
```bash
python video_analysis/examples/video_analyzer_app.py
```

2. Use the interface to:
   - Upload a video file
   - Run analysis
   - View results
   - Save analysis to file

## Dependencies

- PyQt6 for GUI
- OpenAI Whisper for audio transcription
- CLIP for visual analysis
- OpenCV for video processing
- PyTorch for deep learning models

## Project Structure

```
video_analysis/
├── examples/
│   ├── video_analyzer_app.py    # Main GUI application
│   └── test_clip_analyzer.py    # Core analysis logic
├── tools/
│   ├── audio_tools/            # Audio processing tools
│   └── video_tools/            # Video processing tools
└── uploads/                    # Directory for uploaded videos
```

## License

MIT License
