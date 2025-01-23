from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
import numpy as np
from pathlib import Path

def create_test_video():
    # Create output directory
    output_dir = Path(__file__).parent / "test_videos"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_video.mp4"

    # Create a background clip (3 seconds, 30 fps)
    bg_clip = ColorClip(size=(640, 480), color=(255, 255, 255), duration=3)
    
    # Create text clips
    text1 = TextClip("Test Video", fontsize=70, color='black', duration=1)
    text2 = TextClip("Frame 2", fontsize=70, color='black', duration=1)
    text3 = TextClip("Frame 3", fontsize=70, color='black', duration=1)
    
    # Position text clips in the center
    text1 = text1.set_position('center').set_start(0)
    text2 = text2.set_position('center').set_start(1)
    text3 = text3.set_position('center').set_start(2)
    
    # Combine clips
    video = CompositeVideoClip([bg_clip, text1, text2, text3])
    
    # Write video
    video.write_videofile(str(output_path), fps=30)
    return output_path

if __name__ == "__main__":
    output_path = create_test_video()
    print(f"Created test video at: {output_path}")
