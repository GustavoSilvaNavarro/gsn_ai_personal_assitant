import sounddevice as sd
import wave
from io import BytesIO
import sys
import time
import numpy as np
from .input_listeners import InputListener

# TODO: Big todo figure out if the audio is being saved nicely

def record_until_keypress(hard_limit=10, fs=44100, channels=1):
    """
    Records audio until a key is pressed or a hard time limit is reached.
    """
    print(f"Recording started. Press any key to stop. Hard limit: {hard_limit}s")

    listener = InputListener()
    listener.start()

    frames = []

    def callback(indata, frame_count, time_info, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
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

def play_from_memory(audio_buffer):
    """
    Plays audio from a BytesIO buffer.
    """
    print("Playing back recorded audio...")
    try:
        # Open the in-memory buffer as a wave file
        with wave.open(audio_buffer, 'rb') as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            n_frames = wf.getnframes()

            # Read all audio frames
            audio_data_bytes = wf.readframes(n_frames)

            # Convert bytes to a numpy array
            dtype_map = {1: np.int8, 2: np.int16, 3: np.int32, 4: np.int32}
            audio_data = np.frombuffer(audio_data_bytes, dtype=dtype_map.get(sample_width))

            # Reshape for multi-channel audio
            if n_channels > 1:
                audio_data = audio_data.reshape(-1, n_channels)

            # Play the audio using sounddevice
            sd.play(audio_data, frame_rate)
            sd.wait()  # Wait for playback to finish
            print("Playback finished.")
    except (wave.Error, Exception) as err:
        print(f"Error reading audio data from buffer: {err}")


if __name__ == "__main__":
    audio_buffer = record_until_keypress(hard_limit=10)

    if audio_buffer:
        print(f"Successfully recorded {audio_buffer.getbuffer().nbytes} bytes of audio.")
        # Now, play the audio back
        play_from_memory(audio_buffer)
    else:
        print("No audio was recorded.")
