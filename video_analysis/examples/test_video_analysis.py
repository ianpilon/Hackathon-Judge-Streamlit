import sys
from pathlib import Path
import logging
from pytube import YouTube
import os

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.video_tools.frame_extractor import FrameExtractor
from tools.video_tools.clip_analyzer import CLIPAnalyzer
from tools.audio_tools.whisper_transcriber import WhisperTranscriber
from tools.integration_tools.vector_store import VectorStore
from agents.video_agent import VideoAnalysisAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_youtube_video(url: str, output_path: str) -> str:
    """Download a YouTube video for testing."""
    logger.info(f"Downloading video from {url}")
    yt = YouTube(url)
    video = yt.streams.filter(progressive=True, file_extension='mp4').first()
    return video.download(output_path)

def test_video_analysis(video_path: str):
    """Test video analysis functionality."""
    logger.info("Starting video analysis test")
    
    # Initialize components
    video_agent = VideoAnalysisAgent()
    vector_store = VectorStore()
    
    try:
        # 1. Analyze video content
        logger.info("1. Testing video content analysis")
        video_results = video_agent.analyze_video_content(video_path)
        print("\nVideo Analysis Results:")
        print(f"- Found {video_results['frame_count']} key frames")
        print("- Dominant categories:", 
              [f"{cat}({count})" for cat, count in video_results['summary']['dominant_categories']])
        
        # 2. Test frame extraction
        logger.info("\n2. Testing frame extraction")
        frame_results = video_agent.extract_keyframes(video_path, max_frames=5)
        print("\nFrame Extraction Results:")
        print(f"- Extracted {len(frame_results['frames'])} frames")
        print(f"- Video duration: {frame_results['metadata']['duration']:.2f} seconds")
        
        # 3. Test audio transcription
        logger.info("\n3. Testing audio transcription")
        transcriber = WhisperTranscriber()
        transcription = transcriber.transcribe_audio(video_path)
        print("\nTranscription Results:")
        print(f"- Number of segments: {len(transcription['segments'])}")
        print("- First segment:", transcription['segments'][0]['text'] if transcription['segments'] else "No segments")
        
        # 4. Test vector storage
        logger.info("\n4. Testing vector storage")
        # Get embeddings for first frame
        clip_analyzer = CLIPAnalyzer()
        first_frame = frame_results['frames'][0]
        frame_embedding = clip_analyzer.get_frame_embedding(first_frame)
        
        # Store embeddings
        video_id = Path(video_path).stem
        vector_store.add_frame_embeddings(
            video_id=video_id,
            embeddings=[frame_embedding],
            timestamps=[frame_results['timestamps'][0]],
            metadata=[{'frame_index': 0}]
        )
        
        # Search for similar frames
        search_results = vector_store.search_frames(
            query_embedding=frame_embedding,
            n_results=1,
            video_id=video_id
        )
        print("\nVector Storage Results:")
        print(f"- Successfully stored and retrieved frame embedding")
        print(f"- Search distance: {search_results['distances'][0]:.4f}")
        
        logger.info("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

def main():
    # Create test directory
    test_dir = Path(__file__).parent / "test_videos"
    test_dir.mkdir(exist_ok=True)
    
    # Download a short test video from YouTube
    video_url = "https://www.youtube.com/watch?v=8HyCNIVRbSU"  # 30-second nature video
    video_path = download_youtube_video(video_url, str(test_dir))
    
    # Run tests
    test_video_analysis(video_path)

if __name__ == "__main__":
    main()
