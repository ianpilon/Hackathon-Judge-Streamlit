import streamlit as st
from pathlib import Path
import tempfile
import os
import sys
import cv2
from PIL import Image
import numpy as np
import yt_dlp
import re

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from video_analysis.tools.video_tools.clip_analyzer import CLIPAnalyzer
from video_analysis.tools.audio_tools.whisper_transcriber import WhisperTranscriber

st.set_page_config(
    page_title="Hackathon Judge",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Hackathon Judge")

def analyze_presentation(segments):
    """Analyze presentation segments according to A2A hackathon judging criteria."""
    results = {
        "innovation_and_creativity": {"score": None, "feedback": [], "observable": False},
        "functioning_prototype": {"score": None, "feedback": [], "observable": False},
        "technical_complexity": {"score": None, "feedback": [], "observable": False},
        "business_utility": {"score": None, "feedback": [], "observable": False},
        "presentation_quality": {"score": None, "feedback": [], "observable": False},
        "bonus_integration": {"score": None, "feedback": [], "observable": False}
    }
    
    # Keywords for each category
    a2a_specific_keywords = [
        "agent to agent", "a2a", "agent-to-agent", 
        "between agents", "agent transaction", "agent transfer",
        "autonomous agent", "agent payment", "agent interaction"
    ]
    
    innovation_keywords = [
        "novel", "unique", "innovative", "creative", "new approach", "unconventional",
        "future of a2a", "agent innovation", "agent automation"
    ]
    
    prototype_keywords = [
        "demo", "demonstration", "transaction", "working", "prototype", "live",
        "agent demo", "agent transaction demo", "a2a transfer"
    ]
    
    technical_keywords = [
        "implementation", "architecture", "integration", "api", "backend", "security",
        "authentication", "database", "infrastructure", "technical", "agent protocol",
        "agent communication", "agent interface"
    ]
    
    business_keywords = [
        "market", "problem", "solution", "opportunity", "customer", "user",
        "business case", "roi", "implementation path", "adoption",
        "agent economy", "agent marketplace", "agent use case"
    ]
    
    presentation_keywords = [
        "clear", "organized", "structure", "story", "professional",
        "explanation", "walkthrough", "demonstration"
    ]
    
    integration_keywords = {
        "story": ["story integration", "integrated with story", "using story", "story platform"],
        "fxn": ["fxn integration", "integrated with fxn", "using fxn", "fxn platform"],
        "alliance": ["alliance integration", "integrated with alliance", "using alliance", "alliance platform"],
        "masumi": ["masumi network integration", "integrated with masumi", "using masumi network", "masumi platform"]
    }
    
    # Track evidence for each category
    evidence = {category: [] for category in results.keys()}
    
    # Track if A2A transactions are demonstrated
    has_a2a_focus = False
    a2a_evidence = []
    
    # Track which partners are integrated
    integrated_partners = set()
    
    for segment in segments:
        text = segment['text'].lower()
        timestamp = f"[{int(segment['start'])}s]"
        
        # Check for A2A specific content
        if any(keyword in text for keyword in a2a_specific_keywords):
            has_a2a_focus = True
            a2a_evidence.append(f"{timestamp} {text}")
        
        # Innovation and Creativity (only count if A2A-related)
        if any(keyword in text for keyword in innovation_keywords):
            if any(a2a_kw in text for a2a_kw in a2a_specific_keywords):
                results["innovation_and_creativity"]["observable"] = True
                evidence["innovation_and_creativity"].append(
                    f"{timestamp} {text}"
                )
        
        # Functioning Prototype (must show A2A transaction)
        if any(keyword in text for keyword in prototype_keywords):
            if any(a2a_kw in text for a2a_kw in a2a_specific_keywords):
                results["functioning_prototype"]["observable"] = True
                evidence["functioning_prototype"].append(
                    f"{timestamp} {text}"
                )
            else:
                # Note non-A2A demo as feedback
                results["functioning_prototype"]["feedback"].append(
                    f"{timestamp} Demo shown but not focused on A2A transactions"
                )
        
        # Technical Complexity
        if any(keyword in text for keyword in technical_keywords):
            if any(a2a_kw in text for a2a_kw in a2a_specific_keywords):
                results["technical_complexity"]["observable"] = True
                evidence["technical_complexity"].append(
                    f"{timestamp} {text}"
                )
        
        # Business Utility
        if any(keyword in text for keyword in business_keywords):
            if any(a2a_kw in text for a2a_kw in a2a_specific_keywords):
                results["business_utility"]["observable"] = True
                evidence["business_utility"].append(
                    f"{timestamp} {text}"
                )
        
        # Presentation Quality
        if any(keyword in text for keyword in presentation_keywords):
            results["presentation_quality"]["observable"] = True
            evidence["presentation_quality"].append(
                f"{timestamp} {text}"
            )
        
        # Bonus Integration - Check each partner specifically
        for partner, partner_keywords in integration_keywords.items():
            if any(keyword in text for keyword in partner_keywords):
                results["bonus_integration"]["observable"] = True
                integrated_partners.add(partner)
                evidence["bonus_integration"].append(
                    f"{timestamp} Integration with {partner}: {text}"
                )
    
    # If no A2A focus is found, add warning feedback
    if not has_a2a_focus:
        for category in ["innovation_and_creativity", "functioning_prototype", "technical_complexity", "business_utility"]:
            results[category]["feedback"].append(
                "WARNING: No clear focus on A2A (Agent-to-Agent) transactions detected"
            )
    else:
        # Add A2A evidence as positive feedback
        results["functioning_prototype"]["feedback"].extend([
            "A2A transaction focus detected:",
            *[evidence for evidence in a2a_evidence[:2]]  # Show first 2 pieces of evidence
        ])
    
    # Score only categories with sufficient evidence
    for category, data in results.items():
        if data["observable"]:
            # Base score on amount and quality of evidence
            if category == "bonus_integration":
                # Score based on number of partners integrated
                data["score"] = len(integrated_partners)
                if data["score"] == 0:
                    data["feedback"] = ["No clear integration with event partners detected"]
                else:
                    data["feedback"].append(f"Integrated with {len(integrated_partners)} partners: {', '.join(integrated_partners)}")
            else:
                evidence_count = len(evidence[category])
                if evidence_count > 0:
                    # Score out of 5 points
                    base_score = min(5, evidence_count)
                    
                    # For categories requiring A2A focus, only give full score if A2A is demonstrated
                    if category in ["innovation_and_creativity", "functioning_prototype", "technical_complexity", "business_utility"]:
                        if not has_a2a_focus:
                            base_score = 0  # No points if no A2A focus
                            data["feedback"].append("Score: 0 - Project does not demonstrate A2A transactions")
                        else:
                            data["feedback"].append(f"Score: {base_score} - Shows A2A transaction focus")
                    
                    data["score"] = base_score
                    
                    # Add detailed feedback with timestamps
                    data["feedback"].extend([
                        f"Evidence found: {e}" for e in evidence[category][:3]  # Show top 3 pieces of evidence
                    ])
                else:
                    data["feedback"].append("Insufficient evidence for scoring")
        else:
            data["feedback"].append("No observable evidence in video")
    
    # Calculate total score from validated categories only
    validated_scores = [
        data["score"] for data in results.values() 
        if data["score"] is not None
    ]
    
    if validated_scores:
        results["total_score"] = sum(validated_scores)
        results["categories_scored"] = len(validated_scores)
    else:
        results["total_score"] = 0
        results["categories_scored"] = 0
    
    return results

def process_audio(audio_file):
    """Process audio file for transcription and analysis."""
    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tmp_file.write(audio_file.getvalue())
        audio_path = tmp_file.name

    try:
        with st.spinner('Analyzing presentation...'):
            # Initialize transcriber
            whisper_transcriber = WhisperTranscriber()
            
            # Transcribe audio
            audio_results = whisper_transcriber.transcribe_audio(audio_path)
            
            # Display timestamped segments
            st.subheader("⏱️ Presentation Transcript")
            segments = audio_results.get('segments', [])
            for segment in segments:
                start_time = int(segment['start'])
                end_time = int(segment['end'])
                st.write(f"[{start_time:02d}:{(start_time%60):02d} - {end_time:02d}:{(end_time%60):02d}] {segment['text']}")
            
            # Analyze presentation and display results
            st.subheader("🎯 Hackathon Judge Results")
            results = analyze_presentation(segments)
            
            # Display scores with progress bars
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📊 Scores:")
                for category, data in results.items():
                    if category not in ["total_score", "categories_scored"]:
                        st.write(f"{category.replace('_', ' ').title()}")
                        if data["score"] is not None:
                            st.progress(data["score"] / 5)
                            st.write(f"Score: {data['score']}/5")
                        else:
                            st.write("Score: N/A")
                        st.write("")
            
            with col2:
                st.write("💡 Feedback:")
                for category, data in results.items():
                    if category not in ["total_score", "categories_scored"]:
                        if data["feedback"]:
                            st.write(f"{category.replace('_', ' ').title()}:")
                            for feedback in data["feedback"][:3]:  # Show top 3 feedback items
                                st.write(f"- {feedback}")
                            st.write("")
            
            st.write(f"Total Score: {results['total_score']}")
            st.write(f"Categories Scored: {results['categories_scored']}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(audio_path)

def process_video(video_file):
    """Process video file for transcription and analysis."""
    # Create a temporary file to store the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_file.getvalue())
        video_path = tmp_file.name

    try:
        with st.spinner('Analyzing presentation...'):
            # Initialize transcriber
            whisper_transcriber = WhisperTranscriber()
            
            # Transcribe audio
            audio_results = whisper_transcriber.transcribe_audio(video_path)
            
            # Display timestamped segments
            st.subheader("⏱️ Presentation Transcript")
            segments = audio_results.get('segments', [])
            for segment in segments:
                start_time = int(segment['start'])
                end_time = int(segment['end'])
                st.write(f"[{start_time:02d}:{(start_time%60):02d} - {end_time:02d}:{(end_time%60):02d}] {segment['text']}")
            
            # Analyze presentation and display results
            st.subheader("🎯 Hackathon Judge Results")
            results = analyze_presentation(segments)
            
            # Display scores with progress bars
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📊 Scores:")
                for category, data in results.items():
                    if category not in ["total_score", "categories_scored"]:
                        st.write(f"{category.replace('_', ' ').title()}")
                        if data["score"] is not None:
                            st.progress(data["score"] / 5)
                            st.write(f"Score: {data['score']}/5")
                        else:
                            st.write("Score: N/A")
                        st.write("")
            
            with col2:
                st.write("💡 Feedback:")
                for category, data in results.items():
                    if category not in ["total_score", "categories_scored"]:
                        if data["feedback"]:
                            st.write(f"{category.replace('_', ' ').title()}:")
                            for feedback in data["feedback"][:3]:  # Show top 3 feedback items
                                st.write(f"- {feedback}")
                            st.write("")
            
            st.write(f"Total Score: {results['total_score']}")
            st.write(f"Categories Scored: {results['categories_scored']}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(video_path)

def is_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    match = re.match(youtube_regex, url)
    return bool(match)

def download_youtube_video(url):
    """Download YouTube video and return the path to the temporary file."""
    try:
        with st.spinner('Downloading YouTube video...'):
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, 'video.mp4')
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Best quality MP4
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Check if file exists and has content
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("Failed to download video")
            
            # Create final temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            final_path = temp_file.name
            temp_file.close()
            
            # Copy the file to its final location
            import shutil
            shutil.copy2(output_path, final_path)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            return final_path
            
    except Exception as e:
        st.error(f"Error downloading YouTube video: {str(e)}")
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if 'final_path' in locals() and os.path.exists(final_path):
            os.unlink(final_path)
        return None

# File uploader section
st.write("Upload your hackathon presentation recording or provide a YouTube URL:")
input_type = st.radio("Select input type:", ["Video File", "Audio File", "YouTube URL"])

if input_type == "Video File":
    uploaded_file = st.file_uploader("Upload video", type=['mp4', 'avi', 'mov', 'mkv'])
    if uploaded_file is not None:
        # Display video preview
        st.video(uploaded_file)
        
        # Process button
        if st.button("Analyze Video"):
            process_video(uploaded_file)

elif input_type == "Audio File":
    uploaded_file = st.file_uploader("Upload audio", type=['mp3', 'wav', 'm4a', 'ogg'])
    if uploaded_file is not None:
        # Display audio player
        st.audio(uploaded_file)
        
        # Process button
        if st.button("Analyze Audio"):
            process_audio(uploaded_file)

else:  # YouTube URL
    youtube_url = st.text_input("Enter YouTube URL")
    if youtube_url:
        if is_youtube_url(youtube_url):
            # Display YouTube video
            st.video(youtube_url)
            
            # Process button
            if st.button("Analyze YouTube Video"):
                video_path = download_youtube_video(youtube_url)
                if video_path:
                    try:
                        # Create a file-like object that properly implements getvalue
                        class VideoFile:
                            def __init__(self, video_bytes):
                                self._bytes = video_bytes
                            
                            def getvalue(self):
                                return self._bytes
                        
                        with open(video_path, 'rb') as f:
                            video_bytes = f.read()
                        video_file = VideoFile(video_bytes)
                        process_video(video_file)
                    finally:
                        os.unlink(video_path)
        else:
            st.error("Please enter a valid YouTube URL")
