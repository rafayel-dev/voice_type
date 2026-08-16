import tkinter as tk
from tkinter import ttk
import queue
import sys
import threading
import winsound
from .config import logger, load_settings, save_settings
from .recorder import Recorder
from .transcriber import get_engine_name, transcribe
import pyperclip
import pyautogui
import time
import keyboard

class VoiceTyperApp:
    """Main GUI application for Voice Typer."""
    
    # Transcription history max items
    MAX_HISTORY = 20
    
    def __init__(self):
        self.settings = load_settings()
        self.recorder = Recorder()
        self.recorder.set_level_callback(self._on_audio_level)
        
        self._status_queue = queue.Queue()
        self._history = []
        self._current_language = self.settings.get("language", "bn")
        self.display_mode = 0  # 0: Normal, 1: Compact, 2: Mini
        
        self._build_gui()
        self._setup_hotkeys()
        self._check_queue()
    
    # ─── GUI Construction ────────────────────────────────────────
    
    def _build_gui(self):
        self.root = tk.Tk()
        self.root.title("Voice Typer")
        self.root.geometry("280x280")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        self.root.overrideredirect(True)  # Remove standard OS title bar
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # ── Custom Title Bar ──
        self.title_bar = tk.Frame(self.root, bg="#11111b", relief=tk.FLAT, bd=0)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        
        # Dragging logic
        self.title_bar.bind("<Button-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._do_move)
        
        title_label = tk.Label(
            self.title_bar, text="Voice Typer", bg="#11111b", fg="#bac2de", font=("Segoe UI", 9)
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=4)
        title_label.bind("<Button-1>", self._start_move)
        title_label.bind("<B1-Motion>", self._do_move)
        
        # Close Button
        close_btn = tk.Button(
            self.title_bar, text="✕", font=("Segoe UI", 9, "bold"),
            bg="#11111b", fg="#f38ba8", relief=tk.FLAT,
            activebackground="#f38ba8", activeforeground="#11111b",
            cursor="hand2", command=self._on_closing, bd=0, padx=6
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Compact Toggle Button (placed right next to close button)
        self.compact_btn = tk.Button(
            self.title_bar, text="▲", font=("Segoe UI", 9),
            bg="#11111b", fg="#6c7086", relief=tk.FLAT,
            activebackground="#11111b", activeforeground="#cdd6f4",
            cursor="hand2", command=self._toggle_compact_mode, bd=0, padx=6
        )
        self.compact_btn.pack(side=tk.RIGHT)        
        style = ttk.Style()
        style.theme_use("clam")
        
        # ── Header Frame (Status) ──
        self.header_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.header_frame.pack(fill=tk.X, padx=10, pady=(4, 4))
        
        self.status_label = tk.Label(
            self.header_frame, text="🎙️ Ready", 
            font=("Segoe UI", 13, "bold"), fg="#a6e3a1", bg="#1e1e2e"
        )
        self.status_label.pack(expand=True)
        
        # ── Audio Level Bar ──
        self.level_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.level_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        self.level_canvas = tk.Canvas(
            self.level_frame, height=8, bg="#313244", 
            highlightthickness=0, bd=0
        )
        self.level_canvas.pack(fill=tk.X)
        self.level_bar = self.level_canvas.create_rectangle(0, 0, 0, 8, fill="#89b4fa", outline="")
        
        self.lang_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.lang_frame.pack(pady=2)
        
        self.lang_var = tk.StringVar(value=self._current_language)
        
        for text, value in [("বাংলা", "bn"), ("English", "en")]:
            rb = tk.Radiobutton(
                self.lang_frame, text=text, variable=self.lang_var, value=value,
                font=("Segoe UI", 9), fg="#cdd6f4", bg="#1e1e2e",
                selectcolor="#313244", activebackground="#1e1e2e",
                activeforeground="#cdd6f4", command=self._on_lang_change
            )
            rb.pack(side=tk.LEFT, padx=4)
        
        # ── Start/Stop Button ──
        self.start_btn = tk.Button(
            self.root, text="▶  Start Typing", 
            command=self._on_toggle_click,
            bg="#a6e3a1", fg="#1e1e2e", 
            font=("Segoe UI", 11, "bold"),
            activebackground="#94e2d5", activeforeground="#1e1e2e",
            relief=tk.FLAT, cursor="hand2", padx=15, pady=4
        )
        self.start_btn.pack(pady=6)
        
        # ── Engine Info ──
        engine = get_engine_name()
        self.info_label = tk.Label(
            self.root, 
            text=f"Engine: {engine}  •  Ctrl+Alt+Space",
            font=("Segoe UI", 8), fg="#6c7086", bg="#1e1e2e"
        )
        self.info_label.pack()
        
        # ── History Section ──
        self.history_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        history_label = tk.Label(
            self.history_frame, text="Recent:", 
            font=("Segoe UI", 8, "bold"), fg="#6c7086", bg="#1e1e2e",
            anchor="w"
        )
        history_label.pack(fill=tk.X, padx=10, pady=(6, 0))
        
        self.history_text = tk.Text(
            self.history_frame, height=4, font=("Segoe UI", 8), 
            fg="#bac2de", bg="#313244", 
            relief=tk.FLAT, wrap=tk.WORD, state=tk.DISABLED,
            insertbackground="#cdd6f4", selectbackground="#585b70"
        )
        self.history_text.pack(fill=tk.BOTH, padx=10, pady=(2, 8), expand=True)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _do_move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def _toggle_compact_mode(self):
        self.display_mode = (self.display_mode + 1) % 3
        
        # First hide everything except header
        self.history_frame.pack_forget()
        self.info_label.pack_forget()
        self.start_btn.pack_forget()
        self.lang_frame.pack_forget()
        self.level_frame.pack_forget()
        
        if self.display_mode == 0:
            # Normal Mode (280x280)
            self.level_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
            self.lang_frame.pack(pady=2)
            self.start_btn.pack(pady=6)
            self.info_label.pack()
            self.history_frame.pack(fill=tk.BOTH, expand=True)
            self.root.geometry("280x280")
            self.compact_btn.config(text="▲")
        elif self.display_mode == 1:
            # Compact Mode (280x165)
            self.level_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
            self.lang_frame.pack(pady=2)
            self.start_btn.pack(pady=6)
            self.info_label.pack()
            self.root.geometry("280x165")
            self.compact_btn.config(text="━")
        elif self.display_mode == 2:
            # Mini Widget Mode (170x100)
            self.start_btn.pack(pady=2)
            self.root.geometry("170x100")
            self.compact_btn.config(text="▼")
    
    # ─── Hotkey Setup ────────────────────────────────────────────
    
    def _setup_hotkeys(self):
        try:
            # Universal toggle — works for any language
            keyboard.add_hotkey('ctrl+space', self._on_toggle_click)
            # Language-specific shortcuts (also toggle)
            keyboard.add_hotkey('ctrl+alt+e', lambda: self._on_toggle_with_lang("en"))
            keyboard.add_hotkey('ctrl+alt+b', lambda: self._on_toggle_with_lang("bn"))
            logger.info("Hotkeys registered: Ctrl+Space, Ctrl+Alt+E, Ctrl+Alt+B")
        except Exception as e:
            logger.error("Failed to set up hotkeys: %s", e)
    
    # ─── Event Handlers ─────────────────────────────────────────
    
    def _on_lang_change(self):
        self._current_language = self.lang_var.get()
        self.settings["language"] = self._current_language
        save_settings(self.settings)
        logger.info("Language changed to: %s", self._current_language)
    
    def _on_toggle_with_lang(self, lang):
        """Toggle recording with a specific language override."""
        if not self.recorder.is_recording:
            self.lang_var.set(lang)
            self._current_language = lang
        self._on_toggle_click()
    
    def _on_toggle_click(self):
        """Toggle recording on/off."""
        if self.recorder.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self):
        try:
            started = self.recorder.start()
            if started:
                self._play_sound("start")
                lang_name = {"bn": "বাংলা", "en": "English"}.get(self._current_language, "বাংলা")
                self._update_ui(f"🔴 Recording ({lang_name})...", "#f38ba8", recording=True)
        except Exception as e:
            logger.error("Failed to start recording: %s", e)
            self._update_ui("❌ Mic Error", "#f38ba8")
    
    def _stop_recording(self):
        self._play_sound("stop")
        self._update_ui("⏳ Processing...", "#fab387")
        
        # Run stop + transcribe in background thread
        threading.Thread(target=self._process_recording, daemon=True).start()
    
    def _process_recording(self):
        wav_path = self.recorder.stop()
        
        # Reset level bar
        self._status_queue.put(("level", 0))
        
        if not wav_path:
            self._update_ui("⚠️ No audio captured", "#f9e2af")
            self._reset_after_delay()
            return
        
        try:
            text = transcribe(wav_path, self._current_language)
            
            if text:
                self._type_text(text)
                display = text[:30] + "..." if len(text) > 30 else text
                self._update_ui(f"✅ {display}", "#a6e3a1")
                self._add_to_history(text)
            else:
                self._update_ui("🤷 Didn't catch that", "#f9e2af")
        except Exception as e:
            logger.error("Processing error: %s", e)
            self._update_ui("❌ Error occurred", "#f38ba8")
        finally:
            try:
                import os
                os.remove(wav_path)
            except:
                pass
            self._reset_after_delay()
    
    def _type_text(self, text):
        """Paste text into the active application, then restore clipboard."""
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""
        
        pyperclip.copy(text.strip() + " ")
        time.sleep(0.15)
        pyautogui.hotkey('ctrl', 'v')
        
        # Restore original clipboard after a short delay
        time.sleep(0.3)
        try:
            pyperclip.copy(old_clipboard)
        except:
            pass
        
        logger.info("Text typed successfully (%d chars)", len(text))
    
    # ─── Audio Level Callback ────────────────────────────────────
    
    def _on_audio_level(self, level):
        """Called from recorder thread with mic level 0-100."""
        self._status_queue.put(("level", level))
    
    # ─── History ─────────────────────────────────────────────────
    
    def _add_to_history(self, text):
        self._history.insert(0, text)
        self._history = self._history[:self.MAX_HISTORY]
        self._status_queue.put(("history", None))
    
    def _refresh_history_display(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        for i, entry in enumerate(self._history[:5]):
            prefix = "▸ " if i == 0 else "  "
            self.history_text.insert(tk.END, f"{prefix}{entry}\n")
        self.history_text.config(state=tk.DISABLED)
    
    # ─── Sound Effects ───────────────────────────────────────────
    
    def _play_sound(self, event):
        """Play a short system beep for start/stop feedback."""
        try:
            if event == "start":
                winsound.Beep(800, 150)   # Higher pitch, short
            elif event == "stop":
                winsound.Beep(400, 150)   # Lower pitch, short
        except Exception:
            pass  # winsound only works on Windows
    
    # ─── UI Helpers ──────────────────────────────────────────────
    
    def _update_ui(self, status_text, color, recording=False):
        self._status_queue.put(("status", status_text, color, recording))
    
    def _reset_after_delay(self):
        time.sleep(3)
        if not self.recorder.is_recording:
            self._update_ui("🎙️ Ready", "#a6e3a1")
    
    def _check_queue(self):
        """Process all pending UI updates from the queue."""
        try:
            while True:
                item = self._status_queue.get_nowait()
                
                if item[0] == "status":
                    _, text, color, recording = item
                    self.status_label.config(text=text, fg=color)
                    if recording:
                        self.start_btn.config(text="⏹  Stop Typing", bg="#f38ba8", fg="#1e1e2e")
                    else:
                        self.start_btn.config(text="▶  Start Typing", bg="#a6e3a1", fg="#1e1e2e")
                
                elif item[0] == "level":
                    level = item[1]
                    canvas_width = self.level_canvas.winfo_width()
                    bar_width = int(canvas_width * level / 100)
                    # Color gradient: green → yellow → red
                    if level < 40:
                        color = "#a6e3a1"
                    elif level < 70:
                        color = "#f9e2af"
                    else:
                        color = "#f38ba8"
                    self.level_canvas.coords(self.level_bar, 0, 0, bar_width, 8)
                    self.level_canvas.itemconfig(self.level_bar, fill=color)
                
                elif item[0] == "history":
                    self._refresh_history_display()
                    
        except queue.Empty:
            pass
        self.root.after(50, self._check_queue)
    
    def _on_closing(self):
        if self.recorder.is_recording:
            self.recorder.stop()
        save_settings(self.settings)
        self.root.destroy()
        sys.exit(0)
    
    def run(self):
        logger.info("Voice Typer started. Engine: %s", get_engine_name())
        self.root.mainloop()
