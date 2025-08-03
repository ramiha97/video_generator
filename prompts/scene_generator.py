import openai
import json
import os

def generate_video_plan_from_prompt(user_prompt):
    system_prompt = """
You are an AI video scene planner.

You receive a prompt describing a video that someone wants to generate. Break it down into a list of scenes. Each scene should include:

- scene_number: integer
- description: a vivid, cinematic, emotionally engaging description of what the scene shows. If it is an image, describe the visual in detail. If it's a video, describe the motion or camera style (e.g., drone shot, close-up, slow pan).
- type: "image" (generated via MidJourney) or "video" (generated via Veo3)
- duration: how long the scene should last in seconds (max 10s per scene)
- audio:
    - voiceover: true/false
    - voice_gender: "male" or "female" (based on emotion or tone of story)
    - voice_style: short style like "calm", "serious", "emotional", "hopeful"
    - voice_text: the full text script for the voiceover narration if voiceover is true, otherwise empty string
    - background_music: true/false
    - music_mood: short phrase like "emotional piano", "ambient pad", "dramatic strings"
    - music_description: a detailed description of the background music style, instruments, and mood
    - music_genre: genre of the music
- ffmpeg_effects: list of visual effects (e.g., ["fade_in", "fade_out", "grayscale", "zoom_in"])

🧠 Use your creativity to design emotional and visual impact. Make sure the **descriptions are rich and cinematic**, especially for images.

📏 Keep total duration around 60 seconds unless user specifies otherwise.

📦 Return only valid JSON in the following format:
{
  "scenes": [
    {
      "scene_number": 1,
      "description": "...",
      "type": "image" or "video",
      "duration": 5-10,
      "audio": {
        "voiceover": true/false,
        "voice_gender": "...",
        "voice_style": "...",
        "voice_text": "...",
        "background_music": true/false,
        "music_mood": "...",
        "music_description": "...",
        "music_genre": "..."
      },
      "ffmpeg_effects": ["...", "..."]
    }
  ]
}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.9
    )

    content = response['choices'][0]['message']['content']
    try:
        video_plan = json.loads(content)
        return video_plan
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON. Raw output:\n")
        print(content)
        return None