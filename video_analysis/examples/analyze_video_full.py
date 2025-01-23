import sys
from pathlib import Path
import logging
from collections import Counter
from typing import Dict, List

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.video_tools.frame_extractor import FrameExtractor
from tools.video_tools.clip_analyzer import CLIPAnalyzer
from tools.audio_tools.whisper_transcriber import WhisperTranscriber
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_clip_results(frames_analysis: List[Dict]) -> Dict:
    """Summarize the CLIP analysis results."""
    # Count category occurrences
    category_counts = Counter()
    for analysis in frames_analysis:
        category_counts.update(analysis['top_categories'])
    
    # Get top overall categories
    top_categories = [cat for cat, _ in category_counts.most_common(5)]
    
    return {
        'total_frames': len(frames_analysis),
        'top_categories': top_categories,
        'category_counts': dict(category_counts)
    }

def summarize_transcription(transcription: Dict) -> Dict:
    """Summarize the transcription results."""
    total_duration = max(seg['end'] for seg in transcription['segments'])
    total_text = ' '.join(seg['text'] for seg in transcription['segments'])
    
    return {
        'total_duration': total_duration,
        'segment_count': len(transcription['segments']),
        'full_text': total_text
    }

def main():
    """Analyze both video and audio content of the hackathon submission."""
    logger.info("Starting comprehensive video analysis")
    
    # Get path to video
    video_path = Path(__file__).parent / "test_videos" / "LLM Agents Hackathon Submission - E-comm Data Agent.mp4"
    if not video_path.exists():
        logger.error(f"Video not found at {video_path}")
        return
    
    # Initialize components
    frame_extractor = FrameExtractor()
    clip_analyzer = CLIPAnalyzer()
    whisper_transcriber = WhisperTranscriber()
    
    # Extract and analyze frames
    logger.info("Extracting and analyzing frames...")
    frames, timestamps = frame_extractor.extract_keyframes(str(video_path))
    frames_analysis = []
    
    for frame, ts in zip(frames, timestamps):
        analysis = clip_analyzer.analyze_frame(frame)
        analysis['timestamp'] = ts
        frames_analysis.append(analysis)
    
    # Transcribe audio
    logger.info("Transcribing audio...")
    transcription = whisper_transcriber.transcribe_audio(str(video_path))
    
    # Generate summaries
    clip_summary = summarize_clip_results(frames_analysis)
    transcription_summary = summarize_transcription(transcription)
    
    # Print comprehensive summary
    logger.info("\n=== Video Content Analysis ===")
    logger.info(f"Analyzed {clip_summary['total_frames']} key frames")
    logger.info("\nTop visual categories:")
    for cat in clip_summary['top_categories']:
        count = clip_summary['category_counts'][cat]
        logger.info(f"  - {cat}: appeared in {count} frames")
    
    logger.info("\n=== Audio Content Analysis ===")
    logger.info(f"Duration: {transcription_summary['total_duration']:.1f} seconds")
    logger.info(f"Number of segments: {transcription_summary['segment_count']}")
    logger.info("\nTranscription:")
    logger.info(transcription_summary['full_text'])
    
    logger.info("\nAnalysis completed!")

if __name__ == "__main__":
    main()
