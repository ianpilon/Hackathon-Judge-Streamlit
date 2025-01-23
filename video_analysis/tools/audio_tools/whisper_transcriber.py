import whisper
import torch
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import librosa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Transcribes audio using OpenAI's Whisper model."""
    
    def __init__(self, model_size: str = "base"):
        logger.info(f"Initializing Whisper transcriber with model size: {model_size}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        self.model = whisper.load_model(model_size).to(self.device)
        self.sample_rate = 16000  # Whisper expects 16kHz audio
        self.chunk_length = 30  # default chunk length
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        chunk_size: Optional[int] = None
    ) -> Dict:
        """
        Transcribe audio file with timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code
            chunk_size: Optional chunk size in seconds
            
        Returns:
            Dictionary containing transcription results
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Starting transcription of {audio_path}")
        
        try:
            # Use whisper's built-in audio loading instead of librosa
            result = self.model.transcribe(
                audio_path,
                language=language,
                task='transcribe',
                fp16=torch.cuda.is_available()
            )
            
            if not result or not result.get('text'):
                raise ValueError("No speech detected in audio")
                
            # Format results
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            return {
                'segments': segments,
                'text': result['text'].strip()
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def _split_audio(
        self,
        audio: np.ndarray,
        chunk_size: int
    ) -> List[np.ndarray]:
        """
        Split audio into chunks.
        
        Args:
            audio: Audio array
            chunk_size: Size of chunks in seconds
            
        Returns:
            List of audio chunks
        """
        chunk_length = chunk_size * self.sample_rate
        return [
            audio[i:i + chunk_length]
            for i in range(0, len(audio), chunk_length)
        ]
    
    def _process_chunk_result(
        self,
        result: Dict,
        chunk_start_time: float
    ) -> Dict:
        """Process the result from whisper model."""
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': float(segment['start']) + chunk_start_time,
                'end': float(segment['end']) + chunk_start_time,
                'text': str(segment['text']).strip()
            })
        
        return {
            'segments': segments,
            'text': result['text']
        }
    
    def get_audio_features(
        self,
        audio_path: str,
        feature_type: str = 'mfcc'
    ) -> np.ndarray:
        """
        Extract audio features from file.
        
        Args:
            audio_path: Path to audio file
            feature_type: Type of features to extract ('mfcc' or 'mel')
            
        Returns:
            Numpy array of audio features
        """
        # Load audio
        audio, _ = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        
        if feature_type == 'mfcc':
            features = librosa.feature.mfcc(y=audio, sr=self.sample_rate)
        elif feature_type == 'mel':
            features = librosa.feature.melspectrogram(y=audio, sr=self.sample_rate)
        else:
            raise ValueError(f"Unsupported feature type: {feature_type}")
        
        return features
