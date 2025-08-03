import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Mapping of (gender, style) to VOICE_ID (replace with actual IDs from ElevenLabs Voice Library)
VOICE_ID_MAP = {
    ("male", "calm"): "21m00Tcm4TlvDq8ikWAM",  # Example male calm voice
    ("male", "serious"): "pNInz6obpgDQGcFmaJgB",  # Placeholder, replace with actual ID
    ("male", "emotional"): "ErXwobaYiN019PkySvjV",  # Placeholder, replace with actual ID
    ("male", "hopeful"): "yoZ06aMxZJJ28mfd3POQ",  # Placeholder, replace with actual ID
    ("female", "calm"): "EXAVITQu4vr4xnSDxMaL",  # Placeholder, replace with actual ID
    ("female", "serious"): "Vr2pT6S3t96Z7gT8JaL2",  # Placeholder, replace with actual ID
    ("female", "emotional"): "z9fAnlkpzviPz146aGWa",  # Placeholder, replace with actual ID
    ("female", "hopeful"): "bVMeCyTHy58xNoL34h3p",  # Placeholder, replace with actual ID
}

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default fallback voice (male, calm)

def generate_voiceover(text, unique_id, voice_gender="male", voice_style="calm", save_dir="./assets/audio"):
    """
    Generate a voiceover using ElevenLabs API with specified gender and style.

    Args:
        text (str): The text to convert to speech.
        unique_id (str): Unique identifier for the output file.
        voice_gender (str): Gender of the voice ("male" or "female").
        voice_style (str): Style of the voice (e.g., "calm", "serious", "emotional", "hopeful").
        save_dir (str): Directory to save the audio file.

    Returns:
        str or None: Path to the saved audio file if successful, else None.
    """
    # Select VOICE_ID based on gender and style
    voice_key = (voice_gender.lower(), voice_style.lower())
    voice_id = VOICE_ID_MAP.get(voice_key, DEFAULT_VOICE_ID)
    print(f"Using voice ID {voice_id} for gender={voice_gender}, style={voice_style}")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        os.makedirs(save_dir, exist_ok=True)
        output_path = os.path.join(save_dir, f"{unique_id}_eventlabs.mp3")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Voiceover saved to {output_path}")
        return output_path
    else:
        print(f"Error generating voiceover: {response.status_code}, {response.text}")
        return None