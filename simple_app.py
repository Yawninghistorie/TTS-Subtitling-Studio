#!/usr/bin/env python3
"""
TTS Subtitling Studio - Simple Version
Using tkinter (built-in, no dependencies)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os


class TTSStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS Subtitling Studio")
        self.root.geometry("1000x700")
        
        self.model_path = None
        self.srt_path = None
        self.target_lang = "vi"
        
        self._build_ui()
    
    def _build_ui(self):
        # Title
        tk.Label(self.root, text="TTS Subtitling Studio", font=("Arial", 24, "bold")).pack(pady=15)
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Controls
        left_frame = tk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Model selection
        tk.Label(left_frame, text="1. Select TTS Model", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(left_frame, text="Choose Model Folder", command=self.select_model, height=2).pack(fill=tk.X)
        self.model_label = tk.Label(left_frame, text="No model selected", fg="gray")
        self.model_label.pack(pady=5)
        
        # SRT selection
        tk.Label(left_frame, text="2. Load SRT File", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        tk.Button(left_frame, text="Choose SRT File", command=self.select_srt, height=2).pack(fill=tk.X)
        self.srt_label = tk.Label(left_frame, text="No file selected", fg="gray")
        self.srt_label.pack(pady=5)
        
        # Language selection
        tk.Label(left_frame, text="3. Target Language", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.lang_var = tk.StringVar(value="vi")
        lang_frame = tk.Frame(left_frame)
        lang_frame.pack()
        for lang, name in [("vi", "Vietnamese"), ("en", "English"), ("ja", "Japanese"), ("ko", "Korean")]:
            tk.Radiobutton(lang_frame, text=name, variable=self.lang_var, value=lang).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=30)
        tk.Button(btn_frame, text="Translate", command=self.translate, width=15, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(btn_frame, text="Generate Audio", command=self.generate, width=15, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(btn_frame, text="Export", command=self.export, width=15, bg="#FF9800", fg="white").pack(pady=5)
        
        # Right panel - Subtitle display
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Subtitles", font=("Arial", 12, "bold")).pack()
        self.subtitle_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Arial", 11))
        self.subtitle_text.pack(fill=tk.BOTH, expand=True)
        self.subtitle_text.insert(tk.END, "Subtitles will appear here after loading SRT file...")
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_model(self):
        folder = filedialog.askdirectory(title="Select TTS Model Folder")
        if folder:
            self.model_path = folder
            self.model_label.config(text=folder.split("\\")[-1], fg="black")
            self.status("Model selected: " + folder)
            
            # Check for .onnx files
            onnx_files = [f for f in os.listdir(folder) if f.endswith('.onnx')]
            if onnx_files:
                self.status(f"Found {len(onnx_files)} ONNX model(s)")
            else:
                messagebox.showwarning("Warning", "No .onnx files found in this folder!")
    
    def select_srt(self):
        file = filedialog.askopenfilename(title="Select SRT File", filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])
        if file:
            self.srt_path = file
            self.srt_label.config(text=file.split("\\")[-1], fg="black")
            self.status("SRT file loaded: " + file)
            
            # Load and display subtitles
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.subtitle_text.delete(1.0, tk.END)
                self.subtitle_text.insert(tk.END, content)
                self.status(f"Loaded {len(content)} characters")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load SRT: {e}")
    
    def translate(self):
        if not self.srt_path:
            messagebox.showwarning("Warning", "Please load an SRT file first!")
            return
        self.status("Translating with Gemini...")
        self.target_lang = self.lang_var.get()
        messagebox.showinfo("Info", f"Translation started!\nTarget language: {self.target_lang}\n\n(Translation logic will be added here)")
    
    def generate(self):
        if not self.model_path or not self.srt_path:
            messagebox.showwarning("Warning", "Please load both model and SRT file first!")
            return
        self.status("Generating audio...")
        messagebox.showinfo("Info", "Audio generation started!\n(This will use the TTS model to generate audio)")
    
    def export(self):
        if not self.srt_path:
            messagebox.showwarning("Warning", "No audio to export!")
            return
        output = filedialog.asksaveasfilename(title="Save Audio", defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")])
        if output:
            self.status("Exported to: " + output)
            messagebox.showinfo("Success", f"Audio saved to:\n{output}")
    
    def status(self, msg):
        self.status_label.config(text=msg)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSStudioApp(root)
    root.mainloop()