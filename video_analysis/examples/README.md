# Video Analysis System Examples

This directory contains example scripts demonstrating how to use the video analysis system.

## Available Examples

### 1. Basic System Test (`test_video_analysis.py`)
Tests all core components of the system:
- Frame extraction
- CLIP-based visual analysis
- Whisper-based audio transcription
- Vector storage and retrieval

```bash
python test_video_analysis.py
```

This script will:
1. Download a sample video from YouTube
2. Process it through all system components
3. Display the results of each step

### 2. Content Search (`content_search.py`)
Demonstrates how to search for specific content within videos:
- Custom category detection
- Timestamp identification
- Transcript analysis
- Result storage and retrieval

```bash
python content_search.py
```

This script will:
1. Use the previously downloaded test video
2. Search for specific categories (e.g., person, animal, nature)
3. Generate a detailed analysis report
4. Save results to `analysis_results.json`

## Prerequisites

Before running the examples:
1. Make sure you have installed all required dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Ensure you have sufficient disk space for video downloads and processing

## Example Output

### Test Video Analysis
```
Video Analysis Results:
- Found 15 key frames
- Dominant categories: nature(8), water(6), sky(4)

Frame Extraction Results:
- Extracted 5 frames
- Video duration: 30.5 seconds

Transcription Results:
- Number of segments: 12
- First segment: "The sound of water flowing..."
```

### Content Search
```
Video Analysis Results:
Video Duration: 30.50 seconds

Found Categories:
- nature: found at 8 timestamps
- water: found at 6 timestamps
- sky: found at 4 timestamps

Transcript Summary:
- Word Count: 45
- Segments: 12
```

## Customization

You can modify the examples to:
1. Use different videos
2. Search for custom categories
3. Adjust analysis parameters
4. Change output formats

Check the code comments for more details on available options.
