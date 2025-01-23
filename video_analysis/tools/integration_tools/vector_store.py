import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional, Union
from ...config.settings import settings
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Manages storage and retrieval of vector embeddings using ChromaDB."""
    
    def __init__(self):
        logger.info("Initializing vector store")
        self.client = chromadb.PersistentClient(
            path=str(settings.VECTOR_STORE_PATH),
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Create collections for different types of embeddings
        self.frame_collection = self.client.get_or_create_collection(
            name="frame_embeddings",
            metadata={"description": "Video frame embeddings"}
        )
        
        self.audio_collection = self.client.get_or_create_collection(
            name="audio_embeddings",
            metadata={"description": "Audio segment embeddings"}
        )
    
    def add_frame_embeddings(
        self,
        video_id: str,
        embeddings: List[np.ndarray],
        timestamps: List[float],
        metadata: Optional[List[Dict]] = None
    ) -> None:
        """
        Add frame embeddings to the store.
        
        Args:
            video_id: Unique identifier for the video
            embeddings: List of frame embeddings
            timestamps: List of frame timestamps
            metadata: Optional list of metadata for each frame
        """
        if len(embeddings) != len(timestamps):
            raise ValueError("Number of embeddings must match number of timestamps")
        
        # Prepare IDs and metadata
        ids = [f"{video_id}_frame_{i}" for i in range(len(embeddings))]
        
        if metadata is None:
            metadata = [{} for _ in range(len(embeddings))]
        
        # Add timestamps to metadata
        for i, ts in enumerate(timestamps):
            metadata[i]['timestamp'] = ts
            metadata[i]['video_id'] = video_id
        
        # Add to collection
        self.frame_collection.add(
            embeddings=[emb.tolist() for emb in embeddings],
            ids=ids,
            metadatas=metadata
        )
        
        logger.info(f"Added {len(embeddings)} frame embeddings for video {video_id}")
    
    def add_audio_embeddings(
        self,
        video_id: str,
        embeddings: List[np.ndarray],
        segments: List[Dict],
        metadata: Optional[List[Dict]] = None
    ) -> None:
        """
        Add audio segment embeddings to the store.
        
        Args:
            video_id: Unique identifier for the video
            embeddings: List of audio embeddings
            segments: List of segment information (start, end, text)
            metadata: Optional list of metadata for each segment
        """
        if len(embeddings) != len(segments):
            raise ValueError("Number of embeddings must match number of segments")
        
        # Prepare IDs and metadata
        ids = [f"{video_id}_audio_{i}" for i in range(len(embeddings))]
        
        if metadata is None:
            metadata = [{} for _ in range(len(segments))]
        
        # Add segment info to metadata
        for i, segment in enumerate(segments):
            metadata[i].update(segment)
            metadata[i]['video_id'] = video_id
        
        # Add to collection
        self.audio_collection.add(
            embeddings=[emb.tolist() for emb in embeddings],
            ids=ids,
            metadatas=metadata
        )
        
        logger.info(f"Added {len(embeddings)} audio embeddings for video {video_id}")
    
    def search_frames(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        video_id: Optional[str] = None
    ) -> Dict:
        """
        Search for similar frames.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            video_id: Optional video ID to filter results
            
        Returns:
            Dictionary containing search results
        """
        # Prepare where clause if video_id is specified
        where = {"video_id": video_id} if video_id else None
        
        results = self.frame_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )
        
        return {
            'ids': results['ids'][0],
            'distances': results['distances'][0],
            'metadata': results['metadatas'][0]
        }
    
    def search_audio_segments(
        self,
        query_embedding: np.ndarray,
        n_results: int = 5,
        video_id: Optional[str] = None
    ) -> Dict:
        """
        Search for similar audio segments.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            video_id: Optional video ID to filter results
            
        Returns:
            Dictionary containing search results
        """
        where = {"video_id": video_id} if video_id else None
        
        results = self.audio_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )
        
        return {
            'ids': results['ids'][0],
            'distances': results['distances'][0],
            'metadata': results['metadatas'][0]
        }
    
    def get_video_embeddings(self, video_id: str) -> Dict:
        """
        Retrieve all embeddings for a specific video.
        
        Args:
            video_id: Video identifier
            
        Returns:
            Dictionary containing frame and audio embeddings
        """
        frame_results = self.frame_collection.get(
            where={"video_id": video_id}
        )
        
        audio_results = self.audio_collection.get(
            where={"video_id": video_id}
        )
        
        return {
            'frame_embeddings': frame_results,
            'audio_embeddings': audio_results
        }
