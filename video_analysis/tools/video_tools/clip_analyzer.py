import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from typing import List, Dict, Union
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIPAnalyzer:
    """Analyzes images using OpenAI's CLIP model."""
    
    def __init__(self, model_name: str = settings.CLIP_MODEL_NAME):
        logger.info(f"Initializing CLIP analyzer with model: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # Pre-defined categories for zero-shot classification
        self.base_categories = [
            "person", "vehicle", "animal", "food", "object",
            "indoor scene", "outdoor scene", "text", "action",
            "emotion", "event"
        ]
    
    def analyze_frame(
        self,
        frame: Union[np.ndarray, Image.Image],
        custom_categories: List[str] = None
    ) -> Dict:
        """
        Analyze a single frame using CLIP.
        
        Args:
            frame: Input frame as numpy array or PIL Image
            custom_categories: Optional list of custom categories for classification
            
        Returns:
            Dictionary containing analysis results
        """
        # Convert numpy array to PIL Image if necessary
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame)
        
        # Prepare image
        inputs = self.processor(
            images=frame,
            text=custom_categories or self.base_categories,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        # Get model outputs
        with torch.no_grad():
            outputs = self.model(**inputs)
            image_features = outputs.image_embeds
            text_features = outputs.text_embeds
            
            # Calculate similarity scores
            similarity = torch.nn.functional.cosine_similarity(
                image_features[:, None],
                text_features[None, :],
                dim=-1
            )
            
        # Process results
        categories = custom_categories or self.base_categories
        scores = similarity[0].cpu().numpy()
        
        # Create results dictionary
        results = {
            'embeddings': image_features[0].cpu().numpy(),
            'classifications': [
                {'category': cat, 'score': float(score)}
                for cat, score in zip(categories, scores)
            ],
            'top_categories': [
                categories[idx] for idx in scores.argsort()[-3:][::-1]
            ]
        }
        
        return results
    
    def batch_analyze_frames(
        self,
        frames: List[Union[np.ndarray, Image.Image]],
        custom_categories: List[str] = None,
        batch_size: int = settings.BATCH_SIZE
    ) -> List[Dict]:
        """
        Analyze multiple frames in batches.
        
        Args:
            frames: List of input frames
            custom_categories: Optional list of custom categories
            batch_size: Size of batches for processing
            
        Returns:
            List of dictionaries containing analysis results
        """
        results = []
        
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1}")
            
            batch_results = [self.analyze_frame(frame, custom_categories) 
                           for frame in batch]
            results.extend(batch_results)
        
        return results
    
    def get_frame_embedding(
        self,
        frame: Union[np.ndarray, Image.Image]
    ) -> np.ndarray:
        """
        Get CLIP embedding for a single frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Numpy array containing frame embedding
        """
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame)
            
        inputs = self.processor(
            images=frame,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            
        return image_features[0].cpu().numpy()
