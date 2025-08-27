import sounddevice as sd
import wave
import sys
import time
import numpy as np
from io import BytesIO
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

    if not frames:
        print("No audio frames recorded. Returning empty bytes.")
        return

    recording = np.concatenate(frames, axis=0)
    recording_int16 = (recording * 32767).astype(np.int16)
    print("Recording stopped.")
    return recording_int16.tobytes()


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


if __name__ == "__main__":
    elevenlabs = ElevenLabsManager()
    new_audio = record_new_audio(duration_limit=10)

    if new_audio:
        text = elevenlabs.convert_speech_to_text(audio=new_audio)
        print('The Result of my text ====> ', text)

