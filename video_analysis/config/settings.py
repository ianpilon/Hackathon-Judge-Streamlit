from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Project Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = BASE_DIR / ".cache"
    VECTOR_STORE_PATH: Path = BASE_DIR / "vector_store"
    
    # Model Settings
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    WHISPER_MODEL_SIZE: str = "base"
    IMAGEBIND_MODEL_TYPE: str = "facebook/imagebind-huge"
    
    # Video Processing Settings
    FRAME_SAMPLING_RATE: int = 1  # frames per second
    MAX_FRAME_CACHE: int = 1000   # maximum number of frames to keep in memory
    BATCH_SIZE: int = 32
    
    # Audio Processing Settings
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_LENGTH: int = 30  # seconds
    
    # Vector Store Settings
    VECTOR_DIMENSION: int = 512
    
    # CrewAI Settings
    AGENT_TIMEOUT: int = 600  # seconds
    
    class Config:
        env_file = ".env"
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

# Initialize settings
settings = Settings()
settings.setup_directories()
