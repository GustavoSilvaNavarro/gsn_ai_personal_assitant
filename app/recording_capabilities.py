import sounddevice as sd
import wave
import io
import requests

def record_to_memory(duration=10, fs=44100, channels=1):
    """
    Record audio and return it as a BytesIO object (WAV format).
    """
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16')
    sd.wait()
    print("Done recording.")

    # Save to BytesIO as WAV
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as f:
        f.setnchannels(channels)
        f.setsampwidth(2)  # 16-bit audio
        f.setframerate(fs)
        f.writeframes(recording.tobytes())

    buffer.seek(0)  # reset pointer to beginning
    return buffer


def transcribe_audio(buffer, api_key):
    """
    Send in-memory audio buffer to ElevenLabs transcription API.
    """
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    files = {"file": ("recording.wav", buffer, "audio/wav")}
    response = requests.post(url, headers=headers, files=files)
    return response.json()


if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY"

    # record up to 5 minutes max
    audio_buffer = record_to_memory(duration=30)  # try 30s for test

    result = transcribe_audio(audio_buffer, API_KEY)
    print("Transcription:", result)
