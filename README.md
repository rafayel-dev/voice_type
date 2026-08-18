# Voice Typer 🎙️

A beautiful, standalone desktop widget that uses your microphone to transcribe speech (Bangla and English) and auto-types the text into whichever software you are currently using. 

## Features
- **Standalone Executable:** Fully portable `.exe` for Windows. No installation, API keys, or configurations required!
- **Free Transcription:** Uses the completely free Google Web Speech API for lifetime access without any hidden costs.
- **Global Hotkeys:** Start/Stop dictating from anywhere using keyboard shortcuts, even when the app is running in the background.
- **Cross-App Typing:** Automatically types into your web browser, Microsoft Word, Notepad, IDE, or any other application you have focused.
- **Bilingual:** Out-of-the-box support for both Bangla (Default) and English.
- **Minimize to Tray:** App can run silently in the background via the system tray, keeping your taskbar clean.
- **Mini Widget Mode:** A beautiful custom title bar with multiple widget sizes (Normal, Compact, Mini) to stay out of your way while you work.

## Download & Run (Windows)
The easiest way to use Voice Typer is to download the compiled executable:
1. Go to the **[Releases](https://github.com/rafayel-dev/voice_type/releases)** page on GitHub.
2. Download `Voice Typer.exe`.
3. Double-click the `.exe` file to run it. 
*(Note: If global hotkeys do not work when clicking outside the app, right-click the `.exe` and select **Run as Administrator**).*

## Running from Source
If you wish to run the app from source or modify the code:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rafayel-dev/voice_type.git
   cd voice_type
   ```

2. **Install Python dependencies:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Usage & Hotkeys

Once the application is running, you can use the on-screen buttons or the following global keyboard shortcuts:

*   **`Ctrl + Space`** : Start/Stop recording (Uses currently selected language)
*   **`Ctrl + Alt + B`** : Instantly switch to **Bangla** and start recording
*   **`Ctrl + Alt + E`** : Instantly switch to **English** and start recording
*   **`▲ / ▼ / ━` Button** : Toggle between Normal, Compact, and Mini Widget modes.
