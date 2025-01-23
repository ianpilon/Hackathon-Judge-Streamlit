import sys
from pathlib import Path
import logging
from typing import List, Dict
import json

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.video_tools.frame_extractor import FrameExtractor
from tools.video_tools.clip_analyzer import CLIPAnalyzer
from tools.audio_tools.whisper_transcriber import WhisperTranscriber
from tools.integration_tools.vector_store import VectorStore
from agents.video_agent import VideoAnalysisAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoContentSearch:
    """Search for specific content within videos."""
    
    def __init__(self):
        self.video_agent = VideoAnalysisAgent()
        self.transcriber = WhisperTranscriber()
        self.vector_store = VectorStore()
        self.clip_analyzer = CLIPAnalyzer()
    
    def analyze_video(
        self,
        video_path: str,
        search_categories: List[str] = None,
        store_results: bool = True
    ) -> Dict:
        """
        Analyze video content and optionally store results.
        
        Args:
            video_path: Path to video file
            search_categories: Optional list of categories to search for
            store_results: Whether to store results in vector store
            
        Returns:
            Dictionary containing analysis results
        """
        video_id = Path(video_path).stem
        logger.info(f"Analyzing video: {video_id}")
        
        # 1. Extract and analyze frames
        frame_data = self.video_agent.extract_keyframes(video_path)
        frames = frame_data['frames']
        timestamps = frame_data['timestamps']
        
        # 2. Analyze frames with custom categories
        frame_analyses = []
        frame_embeddings = []
        
        for frame in frames:
            analysis = self.clip_analyzer.analyze_frame(
                frame,
                custom_categories=search_categories
            )
            frame_analyses.append(analysis)
            frame_embeddings.append(analysis['embeddings'])
        
        # 3. Transcribe audio
        transcription = self.transcriber.transcribe_audio(video_path)
        
        # 4. Store results if requested
        if store_results:
            # Store frame embeddings
            self.vector_store.add_frame_embeddings(
                video_id=video_id,
                embeddings=frame_embeddings,
                timestamps=timestamps,
                metadata=[
                    {
                        'frame_index': i,
                        'categories': analysis['top_categories']
                    }
                    for i, analysis in enumerate(frame_analyses)
                ]
            )
            
            # Extract and store audio features
            audio_features = self.transcriber.get_audio_features(video_path)
            self.vector_store.add_audio_embeddings(
                video_id=video_id,
                embeddings=[audio_features.flatten()],
                segments=transcription['segments']
            )
        
        # 5. Compile results
        return {
            'video_id': video_id,
            'metadata': frame_data['metadata'],
            'frame_analyses': frame_analyses,
            'transcription': transcription,
            'summary': self._generate_content_summary(
                frame_analyses,
                transcription,
                search_categories
            )
        }
    
    def _generate_content_summary(
        self,
        frame_analyses: List[Dict],
        transcription: Dict,
        search_categories: List[str] = None
    ) -> Dict:
        """Generate a summary of found content."""
        # Analyze visual content
        category_timestamps = {}
        if search_categories:
            for i, analysis in enumerate(frame_analyses):
                for cat_data in analysis['classifications']:
                    if cat_data['category'] in search_categories and cat_data['score'] > 0.5:
                        if cat_data['category'] not in category_timestamps:
                            category_timestamps[cat_data['category']] = []
                        category_timestamps[cat_data['category']].append(
                            frame_analyses[i]['timestamp']
                        )
        
        # Analyze transcript
        transcript_summary = {
            'word_count': sum(len(seg['text'].split()) for seg in transcription['segments']),
            'segment_count': len(transcription['segments']),
            'duration': transcription['segments'][-1]['end'] if transcription['segments'] else 0
        }
        
        return {
            'found_categories': category_timestamps,
            'transcript_summary': transcript_summary
        }

def main():
    # Example usage
    video_path = Path(__file__).parent / "test_videos" / "test_video.mp4"
    if not video_path.exists():
        logger.error(f"Please run test_video_analysis.py first to download the test video")
        return
    
    # Initialize content search
    content_search = VideoContentSearch()
    
    # Define categories to search for
    search_categories = [
        "person", "animal", "nature", "water",
        "trees", "sky", "buildings", "vehicles"
    ]
    
    # Analyze video
    results = content_search.analyze_video(
        str(video_path),
        search_categories=search_categories,
        store_results=True
    )
    
    # Print results
    print("\nVideo Analysis Results:")
    print(f"Video Duration: {results['metadata']['duration']:.2f} seconds")
    print("\nFound Categories:")
    for category, timestamps in results['summary']['found_categories'].items():
        print(f"- {category}: found at {len(timestamps)} timestamps")
    
    print("\nTranscript Summary:")
    print(f"- Word Count: {results['summary']['transcript_summary']['word_count']}")
    print(f"- Segments: {results['summary']['transcript_summary']['segment_count']}")
    
    # Save detailed results to file
    output_file = Path(__file__).parent / "analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
