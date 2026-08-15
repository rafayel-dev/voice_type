import speech_recognition as sr
import keyboard
import pyautogui
import pyperclip
from plyer import notification
import threading
import time
import sys

# Initialize recognizer
r = sr.Recognizer()

def notify(msg):
    try:
        notification.notify(
            title="Voice Typer",
            message=msg,
            timeout=2
        )
    except Exception:
        print(f"Notification: {msg}")

def listen_and_type(language_code, lang_name):
    notify(f"Listening in {lang_name}... Speak now!")
    print(f"[{lang_name}] Listening...")
    
    try:
        with sr.Microphone() as source:
            # Adjust for background noise quickly
            r.adjust_for_ambient_noise(source, duration=0.3)
            # Listen until silence is detected
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
        notify("Processing audio...")
        print("Processing...")
        
        # Free Google Web Speech API (No key required)
        text = r.recognize_google(audio, language=language_code)
        print(f"Transcribed: {text}")
        
        # Backup the current clipboard content
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""
        
        # Copy to clipboard with a trailing space for consecutive typing
        pyperclip.copy(text + " ")
        time.sleep(0.1) # Brief delay to allow clipboard to register
        
        # Simulate Paste (Ctrl+V)
        pyautogui.hotkey('ctrl', 'v')
        
        notify(f"Typed: {text}")
        
    except sr.WaitTimeoutError:
        notify("No speech detected.")
        print("Timeout: No speech detected.")
    except sr.UnknownValueError:
        notify("Could not understand audio.")
        print("Error: Could not understand audio.")
    except Exception as e:
        print(f"Error: {e}")
        notify("An error occurred.")

def on_english_hotkey():
    threading.Thread(target=listen_and_type, args=('en-US', 'English')).start()

def on_bangla_hotkey():
    threading.Thread(target=listen_and_type, args=('bn-BD', 'Bangla')).start()

if __name__ == "__main__":
    print("=====================================")
    print("      Voice Typer is Running!        ")
    print("=====================================")
    print("Global Hotkeys:")
    print("  Ctrl + Alt + E  -> Type in English")
    print("  Ctrl + Alt + B  -> Type in Bangla")
    print("  Esc             -> Exit App")
    print("=====================================")
    
    try:
        # Register global hotkeys
        keyboard.add_hotkey('ctrl+alt+e', on_english_hotkey)
        keyboard.add_hotkey('ctrl+alt+b', on_bangla_hotkey)
        
        # Keep the script running until 'esc' is pressed
        keyboard.wait('esc')
        print("\nExiting Voice Typer...")
    except Exception as e:
        print(f"Error setting up hotkeys: {e}")
        print("Note: On Linux, you may need to run this script as root/sudo for global hotkeys to work.")
        sys.exit(1)
