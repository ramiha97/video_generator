import ffmpeg
import os
import uuid
import traceback

def combine_scenes(scene_files, output_path):
    """
    Combine multiple scenes (videos or images) into a single video.

    Args:
        scene_files (list): List of tuples (file_path, duration_seconds).
        output_path (str): Path to save the final combined video.

    Returns:
        str: Path to the final combined video, or None if an error occurs.
    """
    # Create temporary directory for intermediate files
    temp_dir = "./assets/temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Create a temporary file list for FFmpeg concat
    temp_file_list = os.path.join(temp_dir, f"concat_list_{uuid.uuid4()}.txt")
    temp_files = []

    try:
        with open(temp_file_list, "w") as f:
            for file_path, duration in scene_files:
                if not os.path.exists(file_path):
                    print(f"Error: File {file_path} does not exist")
                    continue

                # Generate unique temporary file name
                temp_video = os.path.join(temp_dir, f"temp_{uuid.uuid4()}.mp4")
                temp_files.append(temp_video)

                try:
                    # Check if input has an audio stream
                    probe = ffmpeg.probe(file_path)
                    has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])

                    # If it's an image, convert to video with specified duration
                    if file_path.endswith(('.jpg', '.png')):
                        (
                            ffmpeg
                            .input(file_path, t=duration)
                            .filter('fps', fps=30)
                            .output(temp_video, c_v='libx264', pix_fmt='yuv420p', s='1280x720', an=1)
                            .run(overwrite_output=True)
                        )
                        # Add silent audio to ensure compatibility
                        silent_audio = ffmpeg.input('anullsrc=channel_layout=stereo:sample_rate=44100', f='lavfi', t=duration)
                        (
                            ffmpeg
                            .input(temp_video)
                            .output(temp_video + '.tmp.mp4', c_v='copy', c_a='aac', ac=2, ar=44100, shortest=1)
                            .run(overwrite_output=True)
                        )
                        os.replace(temp_video + '.tmp.mp4', temp_video)
                    else:
                        # Re-encode video to ensure consistent format
                        stream = ffmpeg.input(file_path)
                        args = {
                            'c_v': 'libx264',
                            'pix_fmt': 'yuv420p',
                            'r': 30,
                            's': '1280x720'
                        }
                        if has_audio:
                            args['c_a'] = 'aac'
                            args['ac'] = 2
                            args['ar'] = 44100
                        else:
                            args['an'] = 1
                        (
                            stream
                            .output(temp_video, **args)
                            .run(overwrite_output=True)
                        )
                        # Add silent audio if no audio stream
                        if not has_audio:
                            silent_audio = ffmpeg.input('anullsrc=channel_layout=stereo:sample_rate=44100', f='lavfi', t=duration)
                            (
                                ffmpeg
                                .input(temp_video)
                                .output(temp_video + '.tmp.mp4', c_v='copy', c_a='aac', ac=2, ar=44100, shortest=1)
                                .run(overwrite_output=True)
                            )
                            os.replace(temp_video + '.tmp.mp4', temp_video)

                    f.write(f"file '{temp_video}'\n")
                except ffmpeg.Error as e:
                    print(f"Error processing {file_path}: {e.stderr.decode()}")
                    continue
                except Exception as e:
                    print(f"Unexpected error processing {file_path}: {str(e)}")
                    traceback.print_exc()
                    continue

        if not temp_files:
            print("Error: No valid files to concatenate")
            return None

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Concatenate all files
        try:
            (
                ffmpeg
                .input(temp_file_list, format='concat', safe=0)
                .output(output_path, c_v='libx264', c_a='aac', pix_fmt='yuv420p')
                .run(overwrite_output=True)
            )
            print(f"Final video saved to {output_path}")
            return output_path
        except ffmpeg.Error as e:
            print(f"Error concatenating files: {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"Unexpected error during concatenation: {str(e)}")
            traceback.print_exc()
            return None

    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_list):
            try:
                os.remove(temp_file_list)
            except Exception as e:
                print(f"Error deleting {temp_file_list}: {e}")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Error deleting {temp_file}: {e}")