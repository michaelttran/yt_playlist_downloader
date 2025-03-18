# import ssl
import os
import subprocess
# from pytube import Playlist, YouTube
from pytubefix import Playlist, YouTube
import certifi

# ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

def download_playlist_audio(playlist_url, output_folder='downloads'):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        playlist = Playlist(playlist_url)
    except Exception as e:
        print(f"Failed to initialize playlist: {e}")
        return

    print(f"\nDownloading audio from {len(playlist.video_urls)} videos...\n")

    for video_url in playlist.video_urls:
        try:
            yt = YouTube(video_url)
            print(f"Processing: {yt.title}")

            # Select the highest bitrate audio-only stream available
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            if not audio_stream:
                print(f"❌ No audio stream found for: {yt.title}")
                continue

            # Download the audio file
            audio_file_path = audio_stream.download(output_folder)
            base, ext = os.path.splitext(audio_file_path)
            mp3_file_path = base + '.mp3'

            # If the file is not already an MP3, convert it using FFmpeg
            if ext.lower() != '.mp3':
                print(f"Converting {yt.title} to MP3...")
                command = [
                    'ffmpeg',
                    '-y',              # overwrite without asking
                    '-i', audio_file_path,
                    '-vn',             # no video
                    '-ar', '44100',    # set sample rate
                    '-ac', '2',        # set number of audio channels
                    '-b:a', '192k',    # set audio bitrate
                    mp3_file_path
                ]
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    print(f"❌ FFmpeg conversion failed for {yt.title}.\nError: {result.stderr.decode('utf-8')}")
                    continue

                # Optionally remove the original file after conversion
                os.remove(audio_file_path)
                print(f"✅ Downloaded and converted: {mp3_file_path}")
            else:
                print(f"✅ Downloaded as MP3: {mp3_file_path}")

        except Exception as video_error:
            print(f"❌ Error processing video {video_url}: {video_error}")

    print("\n🎵 All audio files have been successfully downloaded and converted to MP3! 🎵")

if __name__ == '__main__':
    # Replace the URL below with your YouTube playlist URL if needed
    playlist_url = "<youtube_playlist_url>"
    download_playlist_audio(playlist_url)
