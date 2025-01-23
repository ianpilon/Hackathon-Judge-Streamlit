from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import shutil
import os
from typing import Dict
import asyncio
from video_analysis.tools.video_tools.clip_analyzer import ClipAnalyzer
from video_analysis.tools.audio_tools.whisper_transcriber import WhisperTranscriber

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Initialize analyzers
        clip_analyzer = ClipAnalyzer()
        whisper_transcriber = WhisperTranscriber()

        # Process video
        visual_results = await clip_analyzer.analyze(str(file_path))
        audio_results = await whisper_transcriber.transcribe(str(file_path))

        # Clean up
        os.remove(file_path)

        return {
            "visual_analysis": visual_results,
            "audio_analysis": audio_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
