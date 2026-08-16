"""
Voice Typer 🎙️
A desktop application that transcribes speech and auto-types into any app.
Supports English, Bangla, and Auto-Detection.
"""
from voice_typer.gui import VoiceTyperApp

if __name__ == "__main__":
    app = VoiceTyperApp()
    app.run()
