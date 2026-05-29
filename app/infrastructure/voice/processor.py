"""
Voice message processor — placeholder for future implementation.

Future plan:
- Receive OGG/OGA audio from Telegram
- Transcribe via OpenAI Whisper API (whisper-1 model)
- Pass transcribed text to LLM pipeline as regular user message
- Optionally: detect language, validate it's Spanish

Usage (future):
    processor = VoiceProcessor()
    text = await processor.transcribe(audio_bytes, language="es")
"""
from __future__ import annotations


class VoiceProcessor:
    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        raise NotImplementedError(
            "Voice transcription is not implemented in MVP. "
            "Will use OpenAI Whisper API in future versions."
        )

    async def is_spanish(self, text: str) -> bool:
        raise NotImplementedError("Language detection not implemented in MVP.")
