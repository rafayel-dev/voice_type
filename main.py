import speech_recognition as sr
import keyboard
import pyautogui
import pyperclip
import threading
import time
import sys
import tkinter as tk
import queue

# Initialize recognizer
r = sr.Recognizer()
status_queue = queue.Queue()

def update_status(msg, color="black"):
    status_queue.put((msg, color))

def listen_and_type(language_code, lang_name):
    update_status(f"Listening ({lang_name})...", "blue")
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            
        update_status("Processing...", "orange")
        
        text = r.recognize_google(audio, language=language_code)
        
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""
        
        pyperclip.copy(text + " ")
        time.sleep(0.1)
        
        pyautogui.hotkey('ctrl', 'v')
        
        update_status(f"Typed: {text[:20]}...", "green")
        
    except sr.WaitTimeoutError:
        update_status("Timeout: No speech", "red")
    except sr.UnknownValueError:
        update_status("Didn't catch that", "red")
    except Exception as e:
        update_status("Error occurred", "red")
    
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
    
    # Make window small and always on top
    root.geometry("260x80")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    
    # Try to make it a tool window (removes minimize/maximize buttons on Windows)
    try:
        root.attributes("-toolwindow", True)
    except:
        pass

    status_label = tk.Label(root, text="🎙️ Ready", font=("Helvetica", 12, "bold"), fg="black")
    status_label.pack(pady=10)
    
    info_label = tk.Label(root, text="Ctrl+Alt+E (Eng)  |  Ctrl+Alt+B (Ban)", font=("Helvetica", 8), fg="gray")
    info_label.pack()

    def check_queue():
        try:
            while True:
                msg, color = status_queue.get_nowait()
                # If we get a "Ready" message, only apply it if no other events are pending
                if msg == "Ready":
                    if status_queue.empty():
                        status_label.config(text=f"🎙️ {msg}", fg=color)
                else:
                    status_label.config(text=f"🎙️ {msg}", fg=color)
        except queue.Empty:
            pass
        # Check the queue again in 100 milliseconds
        root.after(100, check_queue)

    check_queue()
    
    def on_closing():
        print("Closing Voice Typer...")
        root.destroy()
        sys.exit(0)
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    print("Initializing Voice Typer GUI...")
    try:
        keyboard.add_hotkey('ctrl+alt+e', on_english_hotkey)
        keyboard.add_hotkey('ctrl+alt+b', on_bangla_hotkey)
    except Exception as e:
        print(f"Error setting up hotkeys: {e}")
        print("Note: On Linux, you must run this script with sudo.")
        
    start_gui()
