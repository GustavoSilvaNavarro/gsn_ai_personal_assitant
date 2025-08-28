import sounddevice as sd
import wave
import sys
import time
import numpy as np
from io import BytesIO
from typing import BinaryIO
from .mac_input_listener import InputListener
from .eleven_labs import ElevenLabsManager


def record_new_audio(duration_limit=5, fs=44100, channels=1):
    """
    Records audio for a specified duration or until is stopped by pressing any key and returns the raw audio bytes.

    Args:
        duration_limit (int): Hard duration limit to stop an audio recording.
        fs (int): The sample rate of the audio data.
        channels (int): MacBook Pro Microphone is mono.
    """
    print(f"Recording started. Press any key to stop. Hard limit: {duration_limit}s")
    listener = InputListener()
    listener.start()
    frames = []

    def callback(indata, frame_count, time_info, status):
        if status:
            print(status, file=sys.stderr)
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        start_time = time.time()
        while not listener.is_key_pressed():
            if time.time() - start_time > duration_limit:
                print("\nHard limit reached. Stopping recording.")
                break
            time.sleep(0.01)

    if not len(frames):
        print("No audio frames recorded. Returning empty bytes.")
        return

    recording = np.concatenate(frames, axis=0)
    recording_int16 = (recording * 32767).astype(np.int16)
    print("Recording stopped.")
    return recording_int16.tobytes()


def transform_audio_to_in_memory_wav_file(raw_audio: bytes, fs: int = 44100, channels: int = 1) -> BinaryIO:
    """
    Encapsulates raw audio bytes into an in-memory WAV file format.

    This function takes raw audio data (typically a stream of bytes representing uncompressed audio samples)
    and adds a WAV file header to it. This process creates a valid, playable audio file that is stored
    entirely in memory, represented as an io.BytesIO object. This is useful for passing audio data
    to APIs or other functions that require a file-like object rather than raw bytes.

    The function assumes the raw audio data is a 16-bit PCM stream, which is a standard format for
    uncompressed audio and common with libraries like `sounddevice`.

    Args:
        raw_audio (bytes): The raw audio data as a bytes object.
        fs (int, optional): The sample rate of the audio data in Hertz. Defaults to 44100.
        channels (int, optional): The number of audio channels. Defaults to 1.

    Returns:
        BinaryIO: An in-memory binary stream (BytesIO object) of the WAV file,
                  with the pointer at the beginning of the file.

    Raises:
        wave.Error: If there is an issue writing the audio frames to the buffer.
    """
    try:
        buffer = BytesIO()

        with wave.open(buffer, "wb") as f:
            f.setnchannels(channels)
            f.setsampwidth(2)  # Corresponds to 16-bit audio
            f.setframerate(fs)
            f.writeframes(raw_audio)

        buffer.seek(0)
        return buffer
    except wave.Error as err:
        raise wave.Error(f"Failed to write WAV frames: {err}") from err



def save_audio_to_file(audio_bytes: bytes, filename="recording.wav", fs = 44100, channels = 1):
    """
    Saves raw audio bytes to a WAV file.
    """
    fs = 44100
    channels = 1

    print(f"Saving to {filename}...")

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2) # 16-bit audio
        wf.setframerate(fs)
        wf.writeframes(audio_bytes)

    print("File saved successfully.")


def play_audio_bytes(audio_bytes: bytes, fs=44100):
    """
    Plays back raw audio bytes.

    Args:
        audio_bytes (bytes): The raw audio data as a bytes object.
        fs (int): The sample rate of the audio data.
    """
    print("Replaying audio...")
    # Convert the bytes object back into a NumPy array of int16
    playback_array = np.frombuffer(audio_bytes, dtype=np.int16)

    # Play the NumPy array
    sd.play(playback_array, samplerate=fs)

    # Wait for playback to finish
    sd.wait()
    print("Playback finished.")


def transformation_audio_to_text():
    elevenlabs = ElevenLabsManager()
    # Hard limit 5mins
    new_audio = record_new_audio(duration_limit=5 * 60)

    if not new_audio:
        raise ValueError("Audio could not be recorded, try again later...")

    audio_buffer = transform_audio_to_in_memory_wav_file(raw_audio=new_audio)
    text = elevenlabs.convert_speech_to_text(audio=audio_buffer)

    return text

