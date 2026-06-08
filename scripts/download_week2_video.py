#!/usr/bin/env python3
import subprocess
import json
import time
import sys
import os

NOTEBOOK_ID = "5a520c9c-d47f-4354-95b1-8d208079f55d"
VIDEO_ID = "4c7f1a74-15c2-4b3b-a069-490884619b16"
OUTPUT_PATH = "/Users/andreizelenov/Documents/Projects/AI learning/public/lessons/week-2/video.mp4"

def main():
    print(f"Starting background polling for video {VIDEO_ID}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    start_time = time.time()
    max_seconds = 20 * 60  # 20 minutes limit
    
    while (time.time() - start_time) < max_seconds:
        try:
            result = subprocess.run(
                ["nlm", "studio", "status", NOTEBOOK_ID, "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            items = json.loads(result.stdout)
            target = next((item for item in items if item.get("id") == VIDEO_ID), None)
            
            if target:
                status = target.get("status")
                print(f"[{int(time.time() - start_time)}s elapsed] Status: '{status}'")
                
                if status == "completed":
                    print("✓ Video is completed. Starting download...")
                    subprocess.run([
                        "nlm", "download", "video", NOTEBOOK_ID,
                        "--id", VIDEO_ID,
                        "--output", OUTPUT_PATH
                    ], check=True)
                    print(f"✓ Video saved successfully to {OUTPUT_PATH}!")
                    return
                elif status == "failed":
                    print("✗ Video generation failed in NotebookLM studio.", file=sys.stderr)
                    sys.exit(1)
            else:
                print("✗ Video ID not found in studio list.", file=sys.stderr)
        except Exception as e:
            print(f"Error during poll check: {e}", file=sys.stderr)
            
        time.sleep(30)
        
    print("✗ Polling timed out after 20 minutes.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
