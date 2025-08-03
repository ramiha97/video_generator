import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("VEO3_API_KEY")

def generate_veo3_video(prompt, duration_seconds, unique_id, save_dir="./assets/scenes"):
    """
    Generate a video using Veo3 API and save it locally.

    Args:
        prompt (str): Description for the video generation.
        duration_seconds (int): Duration of the video in seconds (max depends on API limits).
        unique_id (str): Unique identifier for naming the saved video.
        save_dir (str): Directory to save the video file.

    Returns:
        str or None: Path to the saved video file if successful, else None.
    """

    url = "https://api.veo3.com/v1/generate"  # Example endpoint, replace with actual Veo3 API URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "duration": duration_seconds
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Error generating video: {response.status_code} - {response.text}")
        return None

    # Assuming response JSON has a field with direct video URL
    try:
        video_url = response.json().get("video_url")
        if not video_url:
            print("Video URL not found in API response.")
            return None
    except Exception as e:
        print(f"Error parsing response JSON: {e}")
        return None

    # Prepare save directory and filename
    os.makedirs(save_dir, exist_ok=True)
    video_path = os.path.join(save_dir, f"{unique_id}_veo.mp4")

    # Download the video file
    video_resp = requests.get(video_url, stream=True)
    if video_resp.status_code == 200:
        with open(video_path, 'wb') as f:
            for chunk in video_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video saved to {video_path}")
        return video_path
    else:
        print(f"Error downloading video: {video_resp.status_code}")
        return None