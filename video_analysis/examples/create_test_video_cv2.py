import cv2
import numpy as np
from pathlib import Path

def create_test_video():
    # Create output directory
    output_dir = Path(__file__).parent / "test_videos"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_video.mp4"

    # Video settings
    width, height = 640, 480
    fps = 30
    duration = 3  # seconds

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    # Generate frames
    for i in range(fps * duration):
        # Create a white background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add text
        if i < fps:
            text = "Test Video"
        elif i < fps * 2:
            text = "Frame 2"
        else:
            text = "Frame 3"
        
        # Put text on frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 2, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        cv2.putText(frame, text, (text_x, text_y), font, 2, (0, 0, 0), 2)
        
        # Write frame
        out.write(frame)

    # Release video writer
    out.release()
    return output_path

if __name__ == "__main__":
    output_path = create_test_video()
    print(f"Created test video at: {output_path}")
