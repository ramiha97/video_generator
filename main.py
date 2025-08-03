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
from video_processing.scene_processor import process_scene

def main():
    # Load environment variables
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Prompt user for video description
    print("Welcome to the AI Video Generator!")
    user_prompt = input("Please enter a description for your video: ")

    # Generate video plan
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # Set for scene_generator.py
    video_plan = generate_video_plan_from_prompt(user_prompt)
    if not video_plan or "scenes" not in video_plan:
        print("Failed to generate video plan.")
        return

    # Process scenes concurrently
    scene_files = []
    lock = threading.Lock()
    threads = []

    for scene in video_plan["scenes"]:
        thread = threading.Thread(target=process_scene, args=(scene, scene_files, lock))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Combine all scenes into final video
    if scene_files:
        final_output = "./assets/final/final_video.mp4"
        try:
            combine_scenes(scene_files, final_output)
            print(f"Final video saved to {final_output}")
        except Exception as e:
            print(f"Error combining scenes: {e}")
    else:
        print("No scenes were successfully processed.")

if __name__ == "__main__":
    main()