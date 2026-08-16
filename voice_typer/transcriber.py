import os
# pyrefly: ignore [missing-import]
import speech_recognition as sr
from .config import logger

# Initialize engines
_recognizer = sr.Recognizer()

def get_engine_name():
    """Return the name of the active transcription engine."""
    return "Google (Free)"

def transcribe(wav_path, language="auto"):
    """
    Transcribe a WAV file to text using Google Web Speech API.
    
    Args:
        wav_path: Path to a .wav file
        language: "en", "bn", or "auto"
        
    Returns:
        str: The transcribed text, or None if transcription failed.
    """
    try:
        # Google doesn't support "auto" well, default to English if auto is selected
        lang_code = "bn-BD" if language == "bn" else "en-US"
        
        with sr.AudioFile(wav_path) as source:
            audio = _recognizer.record(source)
        
        text = _recognizer.recognize_google(audio, language=lang_code)
        logger.info("Google transcription successful: '%s'", text[:50] if text else "")
        return text.strip() if text else None
        
    except sr.UnknownValueError:
        logger.warning("Google could not understand the audio")
        return None
    except sr.RequestError as e:
        logger.error("Google API request failed: %s", e)
        return None
    except Exception as e:
        logger.error("Google transcription failed: %s", e)
        return None
