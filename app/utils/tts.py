import asyncio
import edge_tts
import os
from typing import Optional
from pathlib import Path

VOICES = ["en-US-GuyNeural"]

# Directory to store audio files
AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)


async def generate_audio(text: str, voice: str, filename: str) -> Path:
    """
    Generates an audio file from the given text and saves it to AUDIO_DIR.

    Args:
        text (str): The text to convert to speech.
        voice (str): The voice to use for TTS.
        filename (str): The name of the output MP3 file.

    Returns:
        Path: The path to the saved audio file.
    """
    if voice not in VOICES:
        raise ValueError(f"Voice '{voice}' is not supported.")

    output_path = AUDIO_DIR / filename
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def extract_text_from_content(content: list) -> Optional[str]:
    """
    Extracts text from the content field.
    Assumes that content is a list of dictionaries with 'type' and 'value' keys.

    Args:
        content (list): A list of dictionaries, each containing 'type' and 'value' keys.

    Returns:
        Optional[str]: A concatenated string of all 'value' fields where 'type' is 'text', 
                    or None if no text is found.
    """
    texts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text" and "value" in item:
            texts.append(item["value"])
    return " ".join(texts) if texts else None


async def generate_and_save_audio(text: str, voice: str, filename: str) -> str:
    """
    Generates an audio file from the provided text and saves it to the file system.

    Args:
        text (str): The text to convert into speech.
        voice (str): The voice to use for Text-to-Speech (TTS).
        filename (str): The name of the output audio file.

    Returns:
        str: The path to the saved audio file.
    """

    audio_path = await generate_audio(text, voice, filename)
    return audio_path