import os
import json
import uuid
import threading
from dotenv import load_dotenv
from prompts.scene_generator import generate_video_plan_from_prompt
from ai_services.LeonardoAi import generate_leonardo_image
from ai_services.veo3 import generate_veo3_video
from ai_services.voiceover import generate_voiceover
from ai_services.music import generate_suno_music_and_save
from ffmpeg_tools.effects import fade_in, fade_out, apply_grayscale, zoom_in, speed_up, add_background_music
from ffmpeg_tools.combine import combine_scenes

def process_scene(scene, scene_files, lock):
    """
    Process a single scene: generate media, voiceover, music, and apply FFmpeg effects.
    Append the result (file_path, duration) to scene_files using a thread-safe lock.

    Args:
        scene (dict): Scene data from the video plan.
        scene_files (list): Shared list to store (file_path, duration) tuples.
        lock (threading.Lock): Lock for thread-safe access to scene_files.
    """
    scene_number = scene["scene_number"]
    unique_id = str(uuid.uuid4())  # Generate unique ID using UUID
    print(f"Processing scene {scene_number} in thread {threading.current_thread().name}...")

    # Generate image or video
    media_path = None
    try:
        if scene["type"] == "image":
            media_path = generate_leonardo_image(
                prompt=scene["description"],
                unique_id=unique_id,
                save_dir="./assets/scenes"
            )
        elif scene["type"] == "video":
            media_path = generate_veo3_video(
                prompt=scene["description"],
                duration_seconds=scene["duration"],
                unique_id=unique_id,
                save_dir="./assets/scenes"
            )
    except Exception as e:
        print(f"Failed to generate media for scene {scene_number}: {e}")
        return

    if not media_path:
        print(f"Failed to generate media for scene {scene_number}")
        return

    # Generate voiceover if specified
    audio_path = None
    if scene["audio"]["voiceover"]:
        try:
            voice_text = scene["audio"]["voice_text"]
            audio_path = generate_voiceover(
                text=voice_text,
                unique_id=f"{unique_id}_voice",
                voice_gender=scene["audio"]["voice_gender"],
                voice_style=scene["audio"]["voice_style"],
                save_dir="./assets/audio"
            )
        except Exception as e:
            print(f"Failed to generate voiceover for scene {scene_number}: {e}")

    # Generate background music if specified
    music_path = None
    if scene["audio"]["background_music"]:
        try:
            music_path = generate_suno_music_and_save(
                prompt=scene["audio"]["music_description"],
                unique_id=f"{unique_id}_music",
                genre=scene["audio"]["music_genre"],
                mood=scene["audio"]["music_mood"],
                duration_seconds=scene["duration"],
                save_dir="./assets/audio"
            )
        except Exception as e:
            print(f"Failed to generate music for scene {scene_number}: {e}")

    # Apply FFmpeg effects
    current_media_path = media_path
    for effect in scene["ffmpeg_effects"]:
        output_path = f"./assets/scenes/{unique_id}_effect_{effect}.mp4"
        try:
            if effect == "fade_in":
                current_media_path = fade_in(current_media_path, duration=2, output_path=output_path)
            elif effect == "fade_out":
                current_media_path = fade_out(current_media_path, duration=2, output_path=output_path)
            elif effect == "grayscale":
                current_media_path = apply_grayscale(current_media_path, output_path=output_path)
            elif effect == "zoom_in":
                current_media_path = zoom_in(current_media_path, zoom_factor=1.5, duration=scene["duration"], output_path=output_path)
            elif effect == "speed_up":
                current_media_path = speed_up(current_media_path, speed_factor=1.2, output_path=output_path)
        except Exception as e:
            print(f"Error applying effect {effect} to scene {scene_number}: {e}")
            continue

    # Combine audio (voiceover and/or music) with video/image
    final_scene_path = f"./assets/scenes/{unique_id}_final.mp4"
    try:
        if audio_path and music_path:
            # First add voiceover
            temp_path = f"./assets/scenes/{unique_id}_temp.mp4"
            add_background_music(current_media_path, audio_path, temp_path, video_volume=1.0, audio_volume=0.7)
            # Then add background music
            add_background_music(temp_path, music_path, final_scene_path, video_volume=1.0, audio_volume=0.3)
        elif audio_path:
            add_background_music(current_media_path, audio_path, final_scene_path, video_volume=1.0, audio_volume=0.7)
        elif music_path:
            add_background_music(current_media_path, music_path, final_scene_path, video_volume=1.0, audio_volume=0.3)
        else:
            final_scene_path = current_media_path
    except Exception as e:
        print(f"Error combining audio for scene {scene_number}: {e}")
        return

    # Append result to scene_files with thread-safe lock
    with lock:
        scene_files.append((final_scene_path, scene["duration"]))