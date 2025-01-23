from setuptools import setup, find_packages

setup(
    name="video_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'crewai>=0.1.0',
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'opencv-python>=4.8.0',
        'openai-whisper>=20231117',
        'pillow>=10.0.0',
        'numpy>=1.24.0',
        'chromadb>=0.4.0',
        'pydantic>=2.0.0',
        'python-dotenv>=1.0.0',
        'pytube>=15.0.0',
        'moviepy>=1.0.3',
        'librosa>=0.10.0',
        'scikit-learn>=1.3.0',
        'tqdm>=4.65.0',
    ],
)
