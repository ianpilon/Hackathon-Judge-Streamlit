import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrameExtractor:
    """Extracts frames from video files with scene detection capabilities."""
    
    def __init__(self, sampling_rate: int = settings.FRAME_SAMPLING_RATE):
        self.sampling_rate = sampling_rate
        self._scene_threshold = 30.0  # Threshold for scene change detection
        
    def extract_keyframes(
        self, 
        video_path: str,
        max_frames: Optional[int] = None
    ) -> Tuple[List[np.ndarray], List[float]]:
        """
        Extract key frames from video with scene detection.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            Tuple containing:
            - List of frames as numpy arrays
            - List of timestamps for each frame
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        frames = []
        timestamps = []
        previous_frame = None
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
        
        logger.info(f"Starting frame extraction from {video_path}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            current_time = frame_count / fps
            
            # Sample frames based on sampling rate
            if frame_count % (fps * self.sampling_rate) != 0:
                continue
                
            # Detect scene change
            if previous_frame is not None:
                if self._is_scene_change(previous_frame, frame):
                    frames.append(frame)
                    timestamps.append(current_time)
                    logger.debug(f"Scene change detected at {current_time:.2f}s")
            else:
                # Always keep first frame
                frames.append(frame)
                timestamps.append(current_time)
            
            previous_frame = frame.copy()
            
            if max_frames and len(frames) >= max_frames:
                logger.info(f"Reached maximum frame limit: {max_frames}")
                break
        
        cap.release()
        logger.info(f"Extracted {len(frames)} frames from video")
        
        return frames, timestamps
    
    def _is_scene_change(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> bool:
        """
        Detect if there is a scene change between two consecutive frames.
        
        Args:
            prev_frame: Previous frame as numpy array
            curr_frame: Current frame as numpy array
            
        Returns:
            Boolean indicating if a scene change was detected
        """
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean squared error between frames
        mse = np.mean((prev_gray - curr_gray) ** 2)
        
        return mse > self._scene_threshold
    
    def get_video_metadata(self, video_path: str) -> dict:
        """
        Get metadata about the video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing video metadata
        """
        cap = cv2.VideoCapture(video_path)
        metadata = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': float(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        }
        cap.release()
        return metadata
