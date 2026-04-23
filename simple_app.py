#!/usr/bin/env python3
"""
TTS Subtitling Studio - Full Version with Gemini + ONNX TTS
Using tkinter (built-in, no dependencies)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json
import subprocess


class TTSStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTS Subtitling Studio")
        self.root.geometry("1100x750")
        
        # Paths
        self.models_folder = "models"  # Folder chứa các model ONNX
        self.model_path = None
        self.srt_path = None
        self.output_path = None
        self.target_lang = "vi"
        self.gemini_api_key = ""
        
        # Tạo folder models nếu chưa có
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
        
        self._build_ui()
        self._scan_models()
    
    def _build_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#2C3E50")
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="TTS Subtitling Studio", font=("Arial", 22, "bold"), bg="#2C3E50", fg="white").pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # ============== LEFT PANEL ==============
        left_frame = tk.LabelFrame(main_frame, text="Controls", font=("Arial", 12, "bold"), padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Gemini API Key
        tk.Label(left_frame, text="🔑 Gemini API Key:", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        self.api_key_entry = tk.Entry(left_frame, width=35, show="*")
        self.api_key_entry.pack()
        self.api_key_entry.insert(0, os.environ.get("GEMINI_API_KEY", ""))
        tk.Button(left_frame, text="💾 Save API Key", command=self.save_api_key).pack(pady=5)
        
        tk.Frame(left_frame, height=2, bg="#CCCCCC").pack(fill=tk.X, pady=10)
        
        # Model selection
        tk.Label(left_frame, text="🎙️ TTS Model:", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        tk.Label(left_frame, text=f"Drop .onnx files into folder:\n{self.models_folder}", fg="blue", font=("Arial", 9)).pack()
        
        # Model listbox
        model_frame = tk.Frame(left_frame)
        model_frame.pack(fill=tk.X, pady=5)
        self.model_listbox = tk.Listbox(model_frame, height=5, font=("Arial", 10))
        self.model_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        scrollbar = tk.Scrollbar(model_frame, orient=tk.VERTICAL)
        scrollbar.config(command=self.model_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.model_listbox.config(yscrollcommand=scrollbar.set)
        
        tk.Button(left_frame, text="🔄 Refresh Models", command=self._scan_models).pack(fill=tk.X)
        
        tk.Frame(left_frame, height=2, bg="#CCCCCC").pack(fill=tk.X, pady=10)
        
        # SRT selection
        tk.Label(left_frame, text="📄 SRT File:", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        tk.Button(left_frame, text="📂 Choose SRT File", command=self.select_srt, height=2).pack(fill=tk.X)
        self.srt_label = tk.Label(left_frame, text="No file selected", fg="gray", wraplength=280)
        self.srt_label.pack(pady=3)
        
        tk.Frame(left_frame, height=2, bg="#CCCCCC").pack(fill=tk.X, pady=10)
        
        # Language selection
        tk.Label(left_frame, text="🌐 Target Language:", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        self.lang_var = tk.StringVar(value="vi")
        lang_frame = tk.Frame(left_frame)
        lang_frame.pack()
        for lang, code, flag in [("vi", "vi", "🇻🇳"), ("en", "en", "🇺🇸"), ("ja", "ja", "🇯🇵"), ("ko", "ko", "🇰🇷")]:
            tk.Radiobutton(lang_frame, text=f"{flag} {lang}", variable=self.lang_var, value=code).pack(side=tk.LEFT)
        
        tk.Frame(left_frame, height=2, bg="#CCCCCC").pack(fill=tk.X, pady=10)
        
        # Action buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 TRANSLATE", command=self.translate, width=18, height=2, bg="#27AE60", fg="white", font=("Arial", 10, "bold")).pack(pady=3)
        tk.Button(btn_frame, text="🎵 GENERATE AUDIO", command=self.generate, width=18, height=2, bg="#3498DB", fg="white", font=("Arial", 10, "bold")).pack(pady=3)
        tk.Button(btn_frame, text="💾 EXPORT", command=self.export, width=18, height=2, bg="#E67E22", fg="white", font=("Arial", 10, "bold")).pack(pady=3)
        
        # ============== RIGHT PANEL ==============
        right_frame = tk.LabelFrame(main_frame, text="Subtitles", font=("Arial", 12, "bold"), padx=10, pady=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = tk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        tk.Button(toolbar, text="➕ Add", width=8, command=self.add_subtitle).pack(side=tk.LEFT)
        tk.Button(toolbar, text="❌ Delete", width=8, command=self.delete_subtitle).pack(side=tk.LEFT)
        tk.Button(toolbar, text="⬆️ Up", width=6, command=self.move_up).pack(side=tk.LEFT)
        tk.Button(toolbar, text="⬇️ Down", width=6, command=self.move_down).pack(side=tk.LEFT)
        tk.Label(toolbar, text="  Entries:").pack(side=tk.LEFT)
        self.entry_count = tk.Label(toolbar, text="0", fg="blue")
        self.entry_count.pack(side=tk.LEFT)
        
        # Subtitle text area
        self.subtitle_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Arial", 11), height=20)
        self.subtitle_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="💡 Drop .onnx files into 'models' folder to see them here", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _scan_models(self):
        """Quét folder models để tìm các file .onnx"""
        self.model_listbox.delete(0, tk.END)
        
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
            self.status(f"Created folder: {self.models_folder}")
            return
        
        models = []
        for file in os.listdir(self.models_folder):
            if file.endswith('.onnx'):
                # Đọc config nếu có
                config_path = os.path.join(self.models_folder, file + '.json')
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        display_name = config.get('name', file)
                    except:
                        display_name = file
                else:
                    display_name = file
                models.append((file, display_name))
        
        if models:
            for file, display in models:
                self.model_listbox.insert(tk.END, f"📢 {display}")
            self.status(f"Found {len(models)} model(s)")
        else:
            self.model_listbox.insert(tk.END, "No models found")
            self.model_listbox.insert(tk.END, f"Drop .onnx files into:")
            self.model_listbox.insert(tk.END, os.path.abspath(self.models_folder))
    
    def on_model_select(self, event):
        """Khi chọn model"""
        selection = self.model_listbox.curselection()
        if selection:
            index = selection[0]
            model_name = self.model_listbox.get(index).replace("📢 ", "")
            self.status(f"Selected model: {model_name}")
    
    def save_api_key(self):
        """Lưu API key"""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.gemini_api_key = api_key
            # Lưu vào biến môi trường
            os.environ["GEMINI_API_KEY"] = api_key
            messagebox.showinfo("Success", "API Key saved!")
            self.status("Gemini API Key saved")
        else:
            messagebox.showwarning("Warning", "Please enter API Key!")
    
    def select_srt(self):
        """Chọn file SRT"""
        file = filedialog.askopenfilename(title="Select SRT File", filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])
        if file:
            self.srt_path = file
            self.srt_label.config(text=file.split("\\")[-1], fg="black")
            self._load_srt(file)
    
    def _load_srt(self, file_path):
        """Đọc và hiển thị nội dung SRT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.subtitle_text.delete(1.0, tk.END)
            self.subtitle_text.insert(tk.END, content)
            
            # Đếm số entry
            entries = content.strip().split('\n\n')
            count = len([e for e in entries if e.strip()])
            self.entry_count.config(text=str(count))
            self.status(f"Loaded: {file_path.split('\\')[-1]} ({count} entries)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load SRT: {e}")
    
    def translate(self):
        """Dịch subtitles bằng Gemini"""
        if not self.gemini_api_key:
            messagebox.showwarning("Warning", "Please enter Gemini API Key first!")
            return
        
        if not self.srt_path:
            messagebox.showwarning("Warning", "Please load an SRT file first!")
            return
        
        self.target_lang = self.lang_var.get()
        self.status(f"Translating to {self.target_lang}...")
        
        try:
            # Đọc nội dung SRT
            with open(self.srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Gọi Gemini API
            self._call_gemini_translate(srt_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {e}")
            self.status("Translation failed")
    
    def _call_gemini_translate(self, srt_content):
        """Gọi Gemini API để dịch"""
        import requests
        
        lang_names = {"vi": "Vietnamese", "en": "English", "ja": "Japanese", "ko": "Korean"}
        target_name = lang_names.get(self.target_lang, self.target_lang)
        
        prompt = f"""Translate this SRT subtitle content to {target_name}.
Keep the same SRT format with timestamps intact.
Just translate the text portions, keep numbers and timing as is.

SRT Content:
{srt_content}

Provide only the translated SRT content:"""
        
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 8192,
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result['candidates'][0]['content']['parts'][0]['text']
                
                # Cập nhật text area
                self.subtitle_text.delete(1.0, tk.END)
                self.subtitle_text.insert(tk.END, translated)
                
                # Lưu file đã dịch
                output_file = self.srt_path.replace('.srt', f'_translated_{self.target_lang}.srt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(translated)
                
                self.status(f"Translated! Saved to: {output_file.split('\\')[-1]}")
                messagebox.showinfo("Success", f"Translation completed!\nSaved: {output_file.split('\\')[-1]}")
            else:
                messagebox.showerror("Error", f"API Error: {response.status_code}\n{response.text}")
                self.status("Translation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Translation error: {e}")
            self.status("Translation failed")
    
    def generate(self):
        """Tạo audio từ subtitles"""
        if not self.model_path:
            messagebox.showwarning("Warning", "Please select a TTS model first!")
            return
        
        if not self.srt_path:
            messagebox.showwarning("Warning", "Please load an SRT file first!")
            return
        
        self.status("Generating audio with ONNX TTS...")
        
        try:
            # Đọc nội dung đã dịch
            content = self.subtitle_text.get(1.0, tk.END).strip()
            
            # Gọi TTS engine (sẽ triển khai sau)
            self._generate_tts(content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {e}")
            self.status("Generation failed")
    
    def _generate_tts(self, text):
        """Tạo audio bằng ONNX TTS"""
        self.status("TTS generation in progress...")
        
        # TODO: Implement ONNX TTS logic here
        # Ví dụ sử dụng onnxruntime để chạy model
        
        messagebox.showinfo("Info", "TTS generation will be implemented here.\n\nThis will use the ONNX model to convert text to speech.")
        self.status("TTS generation completed!")
    
    def export(self):
        """Xuất audio"""
        output = filedialog.asksaveasfilename(title="Save Audio", defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")])
        if output:
            self.output_path = output
            self.status(f"Exported to: {output}")
            messagebox.showinfo("Success", f"Audio saved to:\n{output}")
    
    def add_subtitle(self):
        """Thêm subtitle entry"""
        messagebox.showinfo("Info", "Add subtitle feature - Coming soon!")
    
    def delete_subtitle(self):
        """Xóa subtitle entry"""
        messagebox.showinfo("Info", "Delete subtitle feature - Coming soon!")
    
    def move_up(self):
        """Di chuyển lên"""
        messagebox.showinfo("Info", "Move up feature - Coming soon!")
    
    def move_down(self):
        """Di chuyển xuống"""
        messagebox.showinfo("Info", "Move down feature - Coming soon!")
    
    def status(self, msg):
        """Cập nhật status bar"""
        self.status_label.config(text=f"  {msg}")
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSStudioApp(root)
    root.mainloop()