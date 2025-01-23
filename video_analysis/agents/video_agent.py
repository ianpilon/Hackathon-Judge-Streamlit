from crewai import Agent
from ..tools.video_tools.clip_analyzer import CLIPAnalyzer
from ..tools.video_tools.frame_extractor import FrameExtractor
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAnalysisAgent:
    """Agent responsible for video analysis tasks."""
    
    def __init__(self):
        self.clip_analyzer = CLIPAnalyzer()
        self.frame_extractor = FrameExtractor()
        
    def create_agent(self) -> Agent:
        """
        Create a CrewAI agent for video analysis.
        
        Returns:
            CrewAI Agent instance
        """
        return Agent(
            role='Video Analysis Specialist',
            goal='Extract and analyze visual information from video content',
            backstory="""You are an expert in computer vision and video analysis. 
                        Your job is to extract meaningful visual information from videos,
                        identify objects, scenes, and actions, and provide detailed
                        analysis of visual content.""",
            tools=[
                self.analyze_video_content,
                self.extract_keyframes,
                self.analyze_specific_frame
            ],
            verbose=True
        )
    
    def analyze_video_content(self, video_path: str) -> Dict:
        """
        Analyze the content of a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting video content analysis for {video_path}")
        
        try:
            # Extract frames
            frames, timestamps = self.frame_extractor.extract_keyframes(video_path)
            logger.info(f"Extracted {len(frames)} keyframes")
            
            # Get video metadata
            metadata = self.frame_extractor.get_video_metadata(video_path)
            
            # Analyze frames
            frame_analyses = self.clip_analyzer.batch_analyze_frames(frames)
            
            # Combine results
            results = {
                'metadata': metadata,
                'frame_count': len(frames),
                'timestamps': timestamps,
                'frame_analyses': frame_analyses,
                'summary': self._generate_video_summary(frame_analyses)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing video content: {str(e)}")
            raise
    
    def extract_keyframes(
        self,
        video_path: str,
        max_frames: int = None
    ) -> Dict:
        """
        Extract key frames from a video.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            
        Returns:
            Dictionary containing extracted frames and metadata
        """
        try:
            frames, timestamps = self.frame_extractor.extract_keyframes(
                video_path,
                max_frames=max_frames
            )
            
            metadata = self.frame_extractor.get_video_metadata(video_path)
            
            return {
                'frames': frames,
                'timestamps': timestamps,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {str(e)}")
            raise
    
    def analyze_specific_frame(
        self,
        frame,
        custom_categories: List[str] = None
    ) -> Dict:
        """
        Analyze a specific frame.
        
        Args:
            frame: Frame to analyze
            custom_categories: Optional custom categories for classification
            
        Returns:
            Dictionary containing frame analysis results
        """
        try:
            return self.clip_analyzer.analyze_frame(
                frame,
                custom_categories=custom_categories
            )
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            raise
    
    def _generate_video_summary(self, frame_analyses: List[Dict]) -> Dict:
        """
        Generate a summary of video content based on frame analyses.
        
        Args:
            frame_analyses: List of frame analysis results
            
        Returns:
            Dictionary containing video content summary
        """
        # Collect all detected categories
        all_categories = []
        for analysis in frame_analyses:
            all_categories.extend(analysis['top_categories'])
        
        # Count category occurrences
        category_counts = {}
        for category in all_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort categories by frequency
        sorted_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'dominant_categories': sorted_categories[:5],
            'total_keyframes': len(frame_analyses),
            'category_distribution': category_counts
        }
