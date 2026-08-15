# Voice Typer 🎙️

A desktop application that uses your microphone to transcribe speech (English and Bangla) and auto-types the text into whichever software you are currently using. 

## Features
- **Global Hotkeys:** Start dictating from anywhere using keyboard shortcuts.
- **Cross-App Typing:** Automatically types into your web browser, Microsoft Word, Notepad, or any other application you have focused.
- **Bilingual:** Out-of-the-box support for both English and Bangla.
- **Free Transcription:** Uses the free Google Web Speech API (no API keys required).

## Requirements
- Python 3.8+
- (Linux Only) System packages: `portaudio19-dev`, `python3-pyaudio`, `xclip`

*Note: This app is designed for Desktop operating systems (Linux, Windows, macOS). It does not work on Android (e.g., Termux) due to Android's strict background keylogging and cross-app interaction restrictions.*

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rafayel-dev/voice_type.git
   cd voice_type
   ```

2. **Install Python dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   *(Or simply run the included `./setup.sh` on Linux)*

## Usage

Run the script as Administrator or root (required for global hotkeys to work properly in the background):
```bash
sudo ./venv/bin/python main.py
```

### Hotkeys
*   **`Ctrl + Alt + E`** : Speak and type in **English**
*   **`Ctrl + Alt + B`** : Speak and type in **Bangla**
*   **`Esc`** : Quit the application

Enjoy typing with your voice!
