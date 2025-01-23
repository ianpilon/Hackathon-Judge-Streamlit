import sys
from pathlib import Path
import logging

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.video_tools.frame_extractor import FrameExtractor
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test frame extraction from our test video."""
    logger.info("Starting frame extractor test")
    
    # Get path to test video
    video_path = Path(__file__).parent / "test_videos" / "test_video.mp4"
    if not video_path.exists():
        logger.error(f"Test video not found at {video_path}")
        return
    
    # Initialize frame extractor
    frame_extractor = FrameExtractor()
    
    # Extract frames
    logger.info(f"Extracting frames from {video_path}")
    frames, timestamps = frame_extractor.extract_keyframes(str(video_path))
    
    logger.info(f"Extracted {len(frames)} frames")
    for i, (frame, ts) in enumerate(zip(frames, timestamps)):
        logger.info(f"Frame {i}: shape={frame.shape}, timestamp={ts:.2f}s")
    
    logger.info("Test completed!")

if __name__ == "__main__":
    main()
