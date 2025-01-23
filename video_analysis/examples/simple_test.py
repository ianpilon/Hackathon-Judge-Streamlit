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
    """Run a simple test of the frame extractor."""
    logger.info("Starting simple test")
    
    # Initialize frame extractor
    frame_extractor = FrameExtractor()
    
    # Print settings to verify they're loaded
    logger.info(f"Settings loaded. Base directory: {settings.BASE_DIR}")
    logger.info(f"Cache directory: {settings.CACHE_DIR}")
    
    logger.info("Test completed!")

if __name__ == "__main__":
    main()
