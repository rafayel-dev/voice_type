import pyaudio
import wave
import tempfile
import threading
import os
from .config import CHUNK, CHANNELS, RATE, logger

class Recorder:
    """Handles microphone recording with thread-safe start/stop toggle."""
    
    def __init__(self):
        self._is_recording = False
        self._lock = threading.Lock()
        self._frames = []
        self._sample_width = None
        self._stream = None
        self._pyaudio = None
        self._record_thread = None
        self._level_callback = None  # GUI callback for audio level
    
    @property
    def is_recording(self):
        return self._is_recording
    
    def set_level_callback(self, callback):
        """Set a callback function that receives audio level (0-100) during recording."""
        self._level_callback = callback
    
    def start(self):
        """Start recording from the microphone. Returns True if started, False if already recording."""
        with self._lock:
            if self._is_recording:
                return False
            self._is_recording = True
        
        self._frames = []
        self._pyaudio = pyaudio.PyAudio()
        
        try:
            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            # Save sample width BEFORE we might terminate PyAudio
            self._sample_width = self._pyaudio.get_sample_size(pyaudio.paInt16)
        except Exception as e:
            logger.error("Failed to open microphone: %s", e)
            self._is_recording = False
            self._pyaudio.terminate()
            self._pyaudio = None
            raise
        
        self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._record_thread.start()
        logger.info("Recording started")
        return True
    
    def stop(self):
        """Stop recording. Returns the path to the recorded WAV file, or None if no audio captured."""
        with self._lock:
            if not self._is_recording:
                return None
            self._is_recording = False
        
        # Wait for record thread to finish
        if self._record_thread:
            self._record_thread.join(timeout=3)
        
        # Clean up stream
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                logger.warning("Error closing stream: %s", e)
            self._stream = None
        
        # Terminate PyAudio
        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None
        
        if not self._frames:
            logger.info("Recording stopped with no audio frames")
            return None
        
        # Write to WAV file
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self._sample_width)
                wf.setframerate(RATE)
                wf.writeframes(b''.join(self._frames))
            
            logger.info("Recording saved: %s (%d frames)", temp_path, len(self._frames))
            return temp_path
        except Exception as e:
            logger.error("Failed to save recording: %s", e)
            return None
    
    def _record_loop(self):
        """Internal loop that reads audio chunks from the mic."""
        while self._is_recording:
            try:
                data = self._stream.read(CHUNK, exception_on_overflow=False)
                self._frames.append(data)
                
                # Calculate audio level for the GUI indicator
                if self._level_callback:
                    try:
                        import audioop
                        rms = audioop.rms(data, 2)
                        # Normalize to 0-100 range (max RMS for 16-bit is ~23170)
                        level = min(100, int(rms / 230))
                        self._level_callback(level)
                    except ImportError:
                        # audioop may not be available in Python 3.13+, use manual calc
                        import struct
                        count = len(data) // 2
                        shorts = struct.unpack(f"<{count}h", data)
                        rms = (sum(s * s for s in shorts) / count) ** 0.5
                        level = min(100, int(rms / 230))
                        self._level_callback(level)
                    except Exception:
                        pass
                        
            except Exception as e:
                logger.error("Stream read error: %s", e)
                break
