import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SUNO_API_KEY")

def generate_suno_music_and_save(
    prompt: str,
    unique_id: str,
    api_key: str = API_KEY,
    genre: str = "pop",
    mood: str = "calm",
    duration_seconds: int = 5,
    save_dir: str = "./assets/audio"
) -> str:
    """
    Generate music using Suno AI API from a prompt and style parameters,
    then download and save the audio locally with a unique_id in filename.

    Args:
        prompt (str): The main text prompt describing the music.
        unique_id (str): Unique identifier to name the audio file.
        api_key (str): Your Suno API key.
        genre (str): Genre of the music (e.g., 'pop', 'rock', 'jazz').
        mood (str): Mood of the music (e.g., 'calm', 'energetic').
        duration_seconds (int): Length of generated music clip.
        save_dir (str): Directory to save the audio file.

    Returns:
        str: Path to the saved audio file.
    """

    url = "https://api.suno.ai/v1/generate-music"  # Hypothetical endpoint

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "style": {
            "genre": genre,
            "mood": mood
        },
        "duration_seconds": duration_seconds
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error generating music: {response.status_code} {response.text}")

    data = response.json()
    music_url = data.get("music_url")
    if not music_url:
        raise Exception("No music URL returned in response")

    # Make sure save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Prepare local file path
    local_filename = f"{unique_id}_suno.mp3"
    file_path = os.path.join(save_dir, local_filename)

    # Download the audio content and save locally
    audio_response = requests.get(music_url)
    if audio_response.status_code != 200:
        raise Exception(f"Failed to download audio file: {audio_response.status_code}")

    with open(file_path, "wb") as f:
        f.write(audio_response.content)

    return file_path