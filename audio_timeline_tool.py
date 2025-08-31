# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 19:16:38 2024

@author: mehta
"""

import whisper
import os
from moviepy import VideoFileClip
from datetime import timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import sys

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio/Video Transcription Tool")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.model_size = tk.StringVar(value="base")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Create UI
        self.create_widgets()
        
        # Start checking for messages from worker thread
        self.check_queue()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Audio/Video Transcription Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file_path, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_file).grid(
            row=1, column=2, padx=(5, 0), pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file_path, width=50).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_file).grid(
            row=2, column=2, padx=(5, 0), pady=5)
        
        # Model selection
        ttk.Label(main_frame, text="Model Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        models = [("Tiny (fastest)", "tiny"), ("Base (recommended)", "base"), 
                 ("Small", "small"), ("Medium", "medium"), ("Large (most accurate)", "large")]
        
        for i, (text, value) in enumerate(models):
            ttk.Radiobutton(model_frame, text=text, variable=self.model_size, 
                           value=value).grid(row=0, column=i, padx=(0, 10))
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(20, 5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.transcribe_button = ttk.Button(button_frame, text="Start Transcription", 
                                          command=self.start_transcription, style="Accent.TButton")
        self.transcribe_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)
        
        # Preview text area
        ttk.Label(main_frame, text="Preview:").grid(row=7, column=0, sticky=(tk.W, tk.N), pady=(20, 5))
        
        self.preview_text = scrolledtext.ScrolledText(main_frame, height=15, width=80, 
                                                     wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                              padx=(5, 0), pady=(20, 0))
        
        # Configure text area to expand
        main_frame.rowconfigure(7, weight=1)
        
        # Supported formats info
        info_text = ("Supported formats:\n"
                    "Video: MP4, AVI, MOV, MKV, WMV, FLV, WebM\n"
                    "Audio: MP3, WAV, FLAC, AAC, OGG, M4A")
        ttk.Label(main_frame, text=info_text, font=("Arial", 8), 
                 foreground="gray").grid(row=8, column=0, columnspan=3, pady=(10, 0))
    
    def browse_input_file(self):
        filetypes = [
            ("All supported", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm;*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a"),
            ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.webm"),
            ("Audio files", "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio or Video File",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file_path.set(filename)
            # Auto-generate output filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_name = f"{base_name}_transcript.txt"
            output_path = os.path.join(os.path.dirname(filename), output_name)
            self.output_file_path.set(output_path)
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save Transcript As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.output_file_path.set(filename)
    
    def clear_fields(self):
        self.input_file_path.set("")
        self.output_file_path.set("")
        self.progress_var.set(0)
        self.status_var.set("Ready")
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
    
    def start_transcription(self):
        if not self.input_file_path.get():
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        if not self.output_file_path.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        if not os.path.exists(self.input_file_path.get()):
            messagebox.showerror("Error", "Input file does not exist.")
            return
        
        # Disable the transcribe button
        self.transcribe_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Starting transcription...")
        
        # Start transcription in a separate thread
        thread = threading.Thread(target=self.transcribe_worker)
        thread.daemon = True
        thread.start()
    
    def transcribe_worker(self):
        try:
            # Send progress updates through queue
            self.message_queue.put(("status", "Loading Whisper model..."))
            self.message_queue.put(("progress", 10))
            
            # Load model
            model = whisper.load_model(self.model_size.get())
            
            self.message_queue.put(("status", "Processing file..."))
            self.message_queue.put(("progress", 20))
            
            # Handle video/audio file
            file_path = self.input_file_path.get()
            file_ext = os.path.splitext(file_path)[1].lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
            
            temp_audio_path = None
            
            if file_ext in video_extensions:
                self.message_queue.put(("status", "Extracting audio from video..."))
                self.message_queue.put(("progress", 30))
                
                temp_audio_path = "temp_audio.wav"
                if not self.extract_audio_from_video(file_path, temp_audio_path):
                    self.message_queue.put(("error", "Failed to extract audio from video."))
                    return
                transcribe_path = temp_audio_path
            else:
                transcribe_path = file_path
            
            self.message_queue.put(("status", "Transcribing audio... This may take a while."))
            self.message_queue.put(("progress", 50))
            
            # Transcribe
            result = model.transcribe(
                transcribe_path,
                word_timestamps=True,
                verbose=False
            )
            
            self.message_queue.put(("status", "Saving transcript..."))
            self.message_queue.put(("progress", 90))
            
            # Save results
            self.save_transcript(result, self.output_file_path.get())
            
            # Clean up
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("status", "Transcription completed successfully!"))
            self.message_queue.put(("result", result))
            self.message_queue.put(("success", f"Transcript saved to: {self.output_file_path.get()}"))
            
        except Exception as e:
            self.message_queue.put(("error", f"An error occurred: {str(e)}"))
        finally:
            self.message_queue.put(("enable_button", None))
    
    def check_queue(self):
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "status":
                    self.status_var.set(data)
                elif message_type == "progress":
                    self.progress_var.set(data)
                elif message_type == "error":
                    messagebox.showerror("Error", data)
                    self.status_var.set("Error occurred")
                elif message_type == "success":
                    messagebox.showinfo("Success", data)
                elif message_type == "result":
                    self.show_preview(data)
                elif message_type == "enable_button":
                    self.transcribe_button.config(state=tk.NORMAL)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queue)
    
    def show_preview(self, result):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # Show first few segments as preview
        preview_text = "PREVIEW (First 5 segments):\n" + "="*50 + "\n\n"
        
        for i, segment in enumerate(result['segments'][:5]):
            start_time = self.format_timestamp(segment['start'])
            end_time = self.format_timestamp(segment['end'])
            preview_text += f"[{start_time} --> {end_time}]\n{segment['text'].strip()}\n\n"
        
        if len(result['segments']) > 5:
            preview_text += f"... and {len(result['segments']) - 5} more segments\n\n"
        
        total_duration = self.format_timestamp(result['segments'][-1]['end'])
        preview_text += f"Total Duration: {total_duration}\n"
        preview_text += f"Total Segments: {len(result['segments'])}"
        
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state=tk.DISABLED)
    
    def format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS.mmm format"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{milliseconds:03d}"
    

    def extract_audio_from_video(self, video_path, audio_path):
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(audio_path)
            video.close()
            audio.close()
            return True
        except Exception as e:
            print(f"Error extracting audio: {e}")  # Add this line
            return False
    
    def save_transcript(self, result, output_file):
        """Save transcript with timestamps to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("TRANSCRIPT WITH TIMESTAMPS\n")
            f.write("=" * 50 + "\n\n")
            
            # Write segment-level timestamps
            f.write("SEGMENT-LEVEL TIMESTAMPS:\n")
            f.write("-" * 30 + "\n")
            for segment in result['segments']:
                start_time = self.format_timestamp(segment['start'])
                end_time = self.format_timestamp(segment['end'])
                f.write(f"[{start_time} --> {end_time}] {segment['text'].strip()}\n")
            
            f.write("\n" + "=" * 50 + "\n\n")
            
            # Write word-level timestamps if available
            f.write("WORD-LEVEL TIMESTAMPS:\n")
            f.write("-" * 25 + "\n")
            for segment in result['segments']:
                if 'words' in segment:
                    for word in segment['words']:
                        start_time = self.format_timestamp(word['start'])
                        end_time = self.format_timestamp(word['end'])
                        f.write(f"[{start_time} --> {end_time}] {word['word']}\n")
            
            f.write("\n" + "=" * 50 + "\n\n")
            
            # Write full transcript
            f.write("FULL TRANSCRIPT:\n")
            f.write("-" * 15 + "\n")
            f.write(result['text'])

def main():
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()