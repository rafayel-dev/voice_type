import speech_recognition as sr
import keyboard
import pyautogui
import pyperclip
import threading
import time
import sys
import tkinter as tk
import queue
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    from groq import Groq
    groq_client = Groq(api_key=groq_key)
    print("Groq API Key detected! Using ultra-fast Whisper-Large-v3.")
else:
    groq_client = None
    print("No Groq API Key found. Using free Google Web Speech API.")

# Initialize recognizer and global locks
r = sr.Recognizer()
status_queue = queue.Queue()
is_listening = False
listening_lock = threading.Lock()

def update_status(msg, color="black"):
    status_queue.put((msg, color))

def listen_and_type(language_code, lang_name):
    global is_listening
    
    # Prevent multiple threads from opening the microphone simultaneously
    with listening_lock:
        if is_listening:
            print("Already listening. Ignoring hotkey press.")
            return
        is_listening = True

    try:
        # Map to short language codes for Groq (e.g., 'en' or 'bn')
        short_lang = "en" if "en" in language_code else "bn"
        engine_name = "Groq" if groq_client else "Google"
        
        update_status(f"Listening ({lang_name})...", "blue")
        
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
        update_status(f"Processing ({engine_name})...", "orange")
        
        if groq_client:
            # Use Groq API (Whisper)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav.write(audio.get_wav_data())
                temp_filename = temp_wav.name
                
            try:
                with open(temp_filename, "rb") as file:
                    transcription = groq_client.audio.transcriptions.create(
                      file=(os.path.basename(temp_filename), file.read()),
                      model="whisper-large-v3-1127", # Explicit model fallback 
                      language=short_lang
                    )
                text = transcription.text
            finally:
                os.remove(temp_filename)
        else:
            # Use Google Free API
            text = r.recognize_google(audio, language=language_code)
        
        # Backup the current clipboard content
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""
        
        # Copy to clipboard with a trailing space
        pyperclip.copy(text + " ")
        time.sleep(0.1) 
        
        # Simulate Paste (Ctrl+V)
        pyautogui.hotkey('ctrl', 'v')
        
        update_status(f"Typed: {text[:20]}...", "green")
        
    except sr.WaitTimeoutError:
        update_status("Timeout: No speech", "red")
    except sr.UnknownValueError:
        update_status("Didn't catch that", "red")
    except Exception as e:
        print(f"Error: {e}")
        update_status("Error occurred", "red")
    finally:
        # Release the lock for the next hotkey press
        with listening_lock:
            is_listening = False
        # Reset to ready after 3 seconds
        time.sleep(3)
        update_status("Ready", "black")

def on_english_hotkey():
    threading.Thread(target=listen_and_type, args=('en-US', 'Eng')).start()

def on_bangla_hotkey():
    threading.Thread(target=listen_and_type, args=('bn-BD', 'Ban')).start()

def start_gui():
    root = tk.Tk()
    root.title("Voice Typer")
    
    root.geometry("260x85")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    
    try:
        root.attributes("-toolwindow", True)
    except:
        pass

    engine = "Groq (Whisper)" if groq_client else "Google (Free)"
    
    status_label = tk.Label(root, text="🎙️ Ready", font=("Helvetica", 12, "bold"), fg="black")
    status_label.pack(pady=5)
    
    info_label = tk.Label(root, text=f"Engine: {engine}\nCtrl+Alt+E (Eng)  |  Ctrl+Alt+B (Ban)", font=("Helvetica", 8), fg="gray")
    info_label.pack()

    def check_queue():
        try:
            while True:
                msg, color = status_queue.get_nowait()
                if msg == "Ready":
                    if status_queue.empty() and not is_listening:
                        status_label.config(text=f"🎙️ {msg}", fg=color)
                else:
                    status_label.config(text=f"🎙️ {msg}", fg=color)
        except queue.Empty:
            pass
        root.after(100, check_queue)

    check_queue()
    
    def on_closing():
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    try:
        keyboard.add_hotkey('ctrl+alt+e', on_english_hotkey)
        keyboard.add_hotkey('ctrl+alt+b', on_bangla_hotkey)
    except Exception as e:
        print(f"Error setting up hotkeys: {e}")
        print("Note: On Linux, you must run this script with sudo.")
        
    start_gui()
