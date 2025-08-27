import sounddevice as sd
import wave
from io import BytesIO
import sys
import time
import numpy as np
from .input_listeners import InputListener

# TODO: Big todo figure out if the audio is being saved nicely

def record_until_keypress(hard_limit=10, fs=44100, channels=1, input_device_id=0):
    """
    Records audio until a key is pressed or a hard time limit is reached.
    """
    print(f"Recording started. Press any key to stop. Hard limit: {hard_limit}s")

    listener = InputListener()
    listener.start()

    frames = []

    def callback(indata, frame_count, time_info, status, ):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback, device=input_device_id):
        start_time = time.time()
        while not listener.is_key_pressed():
            if time.time() - start_time > hard_limit:
                print("\nHard limit reached. Stopping recording.")
                break
            time.sleep(0.01) # Small delay to prevent busy-waiting

    # Concatenate all recorded frames into a single NumPy array
    recording = np.concatenate(frames, axis=0)

    # Save the NumPy array to an in-memory BytesIO buffer as a WAV file
    buffer = BytesIO()
    with wave.open(buffer, "wb") as f:
        f.setnchannels(channels)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(recording.tobytes())

    buffer.seek(0)
    print("Recording stopped.")
    return buffer


def record_audio(duration_limit=5, fs = 44100, channels = 1):
    """
    Records audio for a specified duration and returns the raw audio bytes.

    Args:
        duration_limit (int): Hard duration limit to stop an audio recording.
        fs (int): The sample rate of the audio data.
        channels (int): MacBook Pro Microphone is mono.
    """
    print(f"Recording for {duration_limit} seconds...")
    recording = sd.rec(int(duration_limit * fs), samplerate=fs, channels=channels)
    sd.wait()
    print("Recording finished.")

    # Convert the numpy array (float32) to an int16 array
    recording_int16 = (recording * 32767).astype(np.int16)

    # Return the raw bytes
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
    print(sd.query_devices())
    audio = record_audio()
    play_audio_bytes(audio_bytes=audio)

    # if audio_buffer:
    #     save_buffer_to_file(audio_buffer)
    #     print(f"Successfully recorded {audio_buffer.getbuffer().nbytes} bytes of audio.")
    #     # Now, play the audio back
    #     # play_from_memory(audio_buffer)
    # else:
    #     print("No audio was recorded.")


