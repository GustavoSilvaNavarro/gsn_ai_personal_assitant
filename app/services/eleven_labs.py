from elevenlabs.client import ElevenLabs

from app.config import config


class ElevenLabsManager:
    """ElevenLabs service manager."""

    def __init__(self) -> None:  # noqa: D107
        self.elevenlabs = ElevenLabs(api_key=config.ELEVEN_LABS_API_KEY)

    def convert_speech_to_text(self, audio: bytes) -> str:
        """Receives an audio and return the text.

        Args:
            audio: The audio bytes to convert to text.

        Returns:
            str: The transcribed text from the audio.
        """
        transcription = self.elevenlabs.speech_to_text.convert(
            file=audio,
            model_id=config.ELEVEN_LABS_MODEL,
            tag_audio_events=False,  # Tag audio events like laughter, applause, etc.
            language_code="eng",  # Lang of the audio file. If set to None, model will detect the lang automatically.
            diarize=True,  # Whether to annotate who is speaking
        )

        return transcription.text
