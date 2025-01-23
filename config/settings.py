from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    """Application settings."""
    
    # CLIP Model settings
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    
    # Whisper Model settings
    WHISPER_MODEL_NAME: str = "base"
    
    # Processing settings
    BATCH_SIZE: int = 32
    MAX_FRAMES: int = 100
    FRAME_INTERVAL: int = 30  # Process every Nth frame
    
    # Device settings
    FORCE_CPU: bool = False

settings = Settings()
