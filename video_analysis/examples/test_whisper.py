import sys
from pathlib import Path
import logging

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.audio_tools.whisper_transcriber import WhisperTranscriber
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test whisper transcription on our test video."""
    logger.info("Starting whisper transcriber test")
    
    # Get path to test video
    video_path = Path(__file__).parent / "test_videos" / "test_video.mp4"
    if not video_path.exists():
        logger.error(f"Test video not found at {video_path}")
        return
    
    # Initialize whisper transcriber
    transcriber = WhisperTranscriber()
    
    # Transcribe video
    logger.info(f"Transcribing video: {video_path}")
    result = transcriber.transcribe_audio(str(video_path))
    
    # Print results
    logger.info("Transcription results:")
    logger.info(f"Number of segments: {len(result['segments'])}")
    for i, segment in enumerate(result['segments']):
        logger.info(f"Segment {i}:")
        logger.info(f"  Text: {segment['text']}")
        logger.info(f"  Start: {segment['start']:.2f}s")
        logger.info(f"  End: {segment['end']:.2f}s")
    
    logger.info("Test completed!")

if __name__ == "__main__":
    main()
