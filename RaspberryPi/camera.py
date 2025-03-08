import subprocess
from datetime import datetime

def capture_image():
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"/home/bwisni/Pictures/capture_{timestamp}.jpg"
    
    # Capture command (adjust resolution as needed)
    command = [
        "fswebcam",
        "-r", "1280x720",    # Resolution
        "--no-banner",       # Remove default timestamp banner
        "--skip", "2",       # Skip first 2 frames to allow auto-adjust
        filename
    ]
    
    # Execute command
    try:
        subprocess.run(command, check=True)
        print(f"Image captured: {filename}")
        return filename
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")
        return None

if __name__ == "__main__":
    capture_image()