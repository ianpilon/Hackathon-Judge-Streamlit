import sys
from pathlib import Path
import logging

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.video_tools.frame_extractor import FrameExtractor
from tools.video_tools.clip_analyzer import CLIPAnalyzer
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Analyze the hackathon submission video."""
    logger.info("Starting video analysis")
    
    # Get path to test video
    video_path = Path(__file__).parent / "test_videos" / "LLM Agents Hackathon Submission - E-comm Data Agent.mp4"
    if not video_path.exists():
        logger.error(f"Test video not found at {video_path}")
        return
    
    # Initialize components
    frame_extractor = FrameExtractor()
    clip_analyzer = CLIPAnalyzer()
    
    # Extract frames
    logger.info(f"Extracting frames from {video_path}")
    frames, timestamps = frame_extractor.extract_keyframes(str(video_path))
    logger.info(f"Extracted {len(frames)} frames")
    
    # Analyze each frame
    logger.info("Analyzing frames with CLIP")
    for i, (frame, ts) in enumerate(zip(frames, timestamps)):
        # Get frame categories
        analysis = clip_analyzer.analyze_frame(frame)
        
        # Log results
        logger.info(f"\nFrame {i} (timestamp: {ts:.2f}s):")
        logger.info("Top categories:")
        for cat in analysis['top_categories']:
            score = next(c['score'] for c in analysis['classifications'] if c['category'] == cat)
            logger.info(f"  - {cat}: {score:.3f}")
    
    logger.info("\nAnalysis completed!")

if __name__ == "__main__":
    main()
