import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QWidget, QTextEdit, QFileDialog, QLabel,
                            QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logging
from test_clip_analyzer import analyze_video_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisThread(QThread):
    """Thread for running video analysis without blocking the GUI."""
    analysis_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(str, int)  # Message and progress percentage
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
    
    def run(self):
        try:
            def progress_callback(message, percentage):
                self.progress_update.emit(message, percentage)
            
            results = analyze_video_content(Path(self.video_path), progress_callback)
            self.analysis_complete.emit(results)
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}\n"
            error_msg += f"Error type: {type(e).__name__}\n"
            import traceback
            error_msg += f"Traceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
            logger.error(error_msg)
            self.progress_update.emit(error_msg, 0)

class VideoAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Analysis System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create top controls
        controls_layout = QHBoxLayout()
        
        # Left side controls
        left_controls = QHBoxLayout()
        self.upload_btn = QPushButton("Upload Video")
        self.upload_btn.clicked.connect(self.upload_video)
        self.analyze_btn = QPushButton("Analyze Video")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        
        left_controls.addWidget(self.upload_btn)
        left_controls.addWidget(self.analyze_btn)
        
        # Right side controls
        right_controls = QHBoxLayout()
        self.save_btn = QPushButton("Save Results")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        self.new_analysis_btn = QPushButton("New Analysis")
        self.new_analysis_btn.clicked.connect(self.reset_app)
        self.new_analysis_btn.setEnabled(False)
        
        right_controls.addWidget(self.save_btn)
        right_controls.addWidget(self.new_analysis_btn)
        
        # Add stretches to push controls to sides
        controls_layout.addLayout(left_controls)
        controls_layout.addStretch()
        controls_layout.addLayout(right_controls)
        
        layout.addLayout(controls_layout)
        
        # Add status label and progress bar
        self.status_label = QLabel("Upload a video to begin analysis")
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Create results area with two columns
        results_layout = QHBoxLayout()
        
        # General Analysis
        general_layout = QVBoxLayout()
        general_label = QLabel("General Analysis")
        general_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.general_text = QTextEdit()
        self.general_text.setReadOnly(True)
        self.general_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        general_layout.addWidget(general_label)
        general_layout.addWidget(self.general_text)
        results_layout.addLayout(general_layout)
        
        # Hackathon Analysis
        hackathon_layout = QVBoxLayout()
        hackathon_label = QLabel("Hackathon Judging Analysis")
        hackathon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hackathon_text = QTextEdit()
        self.hackathon_text.setReadOnly(True)
        self.hackathon_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        hackathon_layout.addWidget(hackathon_label)
        hackathon_layout.addWidget(self.hackathon_text)
        results_layout.addLayout(hackathon_layout)
        
        layout.addLayout(results_layout)
        
        self.current_video = None
        self.analysis_thread = None
    
    def upload_video(self):
        """Handle video file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            str(Path.home()),
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            self.current_video = file_path
            self.status_label.setText(f"Selected video: {Path(file_path).name}")
            self.analyze_btn.setEnabled(True)
            self.save_btn.setEnabled(False)
            self.new_analysis_btn.setEnabled(True)
    
    def start_analysis(self):
        """Start video analysis in a separate thread."""
        if not self.current_video:
            return
        
        # Disable buttons during analysis
        self.upload_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.new_analysis_btn.setEnabled(False)
        
        # Clear previous results
        self.general_text.clear()
        self.hackathon_text.clear()
        
        # Start analysis in separate thread
        self.analysis_thread = AnalysisThread(self.current_video)
        self.analysis_thread.analysis_complete.connect(self.update_analysis_results)
        self.analysis_thread.progress_update.connect(self.handle_progress_update)
        self.analysis_thread.start()
    
    def save_results(self):
        """Save analysis results to a file."""
        if not hasattr(self, 'current_results'):
            return
            
        # Create default filename from video name
        video_name = Path(self.current_video).stem
        default_filename = f"{video_name}_analysis_{int(time.time())}.txt"
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Results",
            str(Path.home() / default_filename),
            "Text Files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write video information
                f.write("=== Video Analysis Results ===\n")
                f.write(f"Video: {Path(self.current_video).name}\n")
                f.write(f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write general analysis
                f.write("=== General Analysis ===\n")
                f.write(self.general_text.toPlainText())
                f.write("\n\n")
                
                # Write hackathon analysis
                f.write("=== Hackathon Judging Analysis ===\n")
                f.write(self.hackathon_text.toPlainText())
            
            self.status_label.setText(f"Results saved to {file_path}")
        except Exception as e:
            self.status_label.setText(f"Error saving results: {str(e)}")
    
    def reset_app(self):
        """Reset the app for a new analysis."""
        # Clear current video and results
        self.current_video = None
        if hasattr(self, 'current_results'):
            delattr(self, 'current_results')
        
        # Reset UI elements
        self.general_text.clear()
        self.hackathon_text.clear()
        self.status_label.setText("Upload a video to begin analysis")
        self.progress_bar.setValue(0)
        
        # Reset buttons
        self.upload_btn.setEnabled(True)
        self.analyze_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.new_analysis_btn.setEnabled(False)
    
    def update_analysis_results(self, results):
        """Update the UI with analysis results."""
        self.current_results = results
        
        # Display the results
        self.display_results(results)
        
        # Update hackathon analysis text if available
        if "hackathon_analysis" in results:
            self.hackathon_text.setText(results["hackathon_analysis"])
        
        # Enable buttons
        self.analyze_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.new_analysis_btn.setEnabled(True)
    
    def display_results(self, results):
        """Display analysis results in the text area."""
        if not results:
            self.general_text.setText("No results to display")
            return
            
        # Convert dictionary to string if needed
        if isinstance(results, dict):
            text = ""
            if "duration" in results:
                text += f"=== General Video Analysis Summary ===\n"
                text += f"Duration: {results['duration']:.2f} seconds\n"
                text += f"Frames analyzed: {results['frames_analyzed']}\n\n"
            
            if "transcription" in results and results["transcription"]:
                text += "Transcribed content:\n"
                text += results["transcription"]["text"] + "\n\n"
                
                if results["transcription"]["segments"]:
                    text += "Detailed segments:\n"
                    for segment in results["transcription"]["segments"]:
                        text += f"[{segment['start']:.1f}s - {segment['end']:.1f}s]: {segment['text']}\n"
        else:
            text = str(results)
            
        self.general_text.setText(text)
    
    def handle_progress_update(self, message, percentage):
        """Handle progress updates from the analysis thread."""
        self.status_label.setText(message)
        self.progress_bar.setValue(percentage)
        
        if message.startswith("Error") or percentage == 0:
            self.general_text.setText(f"Analysis Error:\n\n{message}")
            self.hackathon_text.clear()
            self.progress_bar.setValue(0)
            self.upload_btn.setEnabled(True)
            self.analyze_btn.setEnabled(True)
            self.save_btn.setEnabled(False)
            self.new_analysis_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = VideoAnalyzerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
