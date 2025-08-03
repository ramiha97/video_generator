import ffmpeg

def fade_in(input_path, duration, output_path):
    """
    Apply fade-in effect at the start of the video.
    duration: seconds of fade-in
    """
    (
        ffmpeg
        .input(input_path)
        .filter('fade', type='in', start_time=0, duration=duration)
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path

def fade_out(input_path, duration, output_path):
    """
    Apply fade-out effect at the end of the video.
    duration: seconds of fade-out
    """
    probe = ffmpeg.probe(input_path)
    video_duration = float(probe['format']['duration'])
    start_time = video_duration - duration

    (
        ffmpeg
        .input(input_path)
        .filter('fade', type='out', start_time=start_time, duration=duration)
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path

def apply_grayscale(input_path, output_path):
    """
    Convert the video to grayscale.
    """
    (
        ffmpeg
        .input(input_path)
        .filter('hue', s=0)
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path

def zoom_in(input_path, zoom_factor, duration, output_path):
    """
    Apply a zoom-in effect over the duration of the video.
    zoom_factor: e.g. 1.5 for 150% zoom
    duration: duration of zoom in seconds
    """
    zoom_expr = f"zoom+{(zoom_factor-1)*'t/{duration}'}"
    # Using zoompan filter for zoom effect - simplified here for demonstration
    (
        ffmpeg
        .input(input_path)
        .filter('zoompan', z='min(zoom+0.0015, {0})'.format(zoom_factor), d=duration*30)  # assuming 30 fps
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path

def speed_up(input_path, speed_factor, output_path):
    """
    Speed up the video by speed_factor.
    speed_factor >1 speeds up, <1 slows down.
    """
    (
        ffmpeg
        .input(input_path)
        .filter('setpts', f'PTS/{speed_factor}')
        .output(output_path)
        .run(overwrite_output=True)
    )
    return output_path

def add_background_music(video_path, audio_path, output_path, video_volume=1.0, audio_volume=0.3):
    """
    Mix background music into video.
    video_volume and audio_volume control the relative volumes.
    """
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)

    video_audio = video.audio.filter('volume', video_volume)
    music_audio = audio.filter('volume', audio_volume)

    mixed_audio = ffmpeg.filter([video_audio, music_audio], 'amix', inputs=2, duration='shortest')

    (
        ffmpeg
        .output(video.video, mixed_audio, output_path, vcodec='copy', acodec='aac', strict='experimental')
        .run(overwrite_output=True)
    )
    return output_path
