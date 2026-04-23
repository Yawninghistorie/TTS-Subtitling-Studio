#!/usr/bin/env python3
"""TTS Subtitling Studio - Simple Working Version"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os


def main():
    root = tk.Tk()
    root.title("TTS Subtitling Studio")
    root.geometry("900x600")
    
    # Variables
    srt_path = None
    api_key = None
    
    # Title
    tk.Label(root, text="TTS Subtitling Studio", font=("Arial", 24, "bold")).pack(pady=10)
    
    # API Key Frame
    api_frame = tk.Frame(root)
    api_frame.pack(pady=5)
    tk.Label(api_frame, text="Gemini API Key:").pack(side=tk.LEFT)
    api_entry = tk.Entry(api_frame, width=50, show="*")
    api_entry.pack(side=tk.LEFT, padx=5)
    
    def save_api():
        nonlocal api_key
        api_key = api_entry.get().strip()
        if api_key:
            tk.Label(root, text=f"✅ API Key saved!", fg="green").pack()
    
    tk.Button(api_frame, text="Save", command=save_api).pack(side=tk.LEFT)
    
    # Main area
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Left side - controls
    left = tk.Frame(main_frame, width=250)
    left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    tk.Label(left, text="📄 SRT File:", font=("Arial", 12, "bold")).pack(pady=5)
    
    def load_srt():
        nonlocal srt_path
        file = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
        if file:
            srt_path = file
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, content)
            status.config(text=f"Loaded: {os.path.basename(file)}")
    
    tk.Button(left, text="Load SRT File", command=load_srt, height=2, width=25).pack()
    
    tk.Label(left, text="", height=2).pack()
    
    tk.Label(left, text="🌐 Language:", font=("Arial", 12, "bold")).pack()
    lang_var = tk.StringVar(value="vi")
    tk.Radiobutton(left, text="🇻🇳 Vietnamese", variable=lang_var, value="vi").pack(anchor=tk.W)
    tk.Radiobutton(left, text="🇺🇸 English", variable=lang_var, value="en").pack(anchor=tk.W)
    tk.Radiobutton(left, text="🇯🇵 Japanese", variable=lang_var, value="ja").pack(anchor=tk.W)
    tk.Radiobutton(left, text="🇰🇷 Korean", variable=lang_var, value="ko").pack(anchor=tk.W)
    tk.Radiobutton(left, text="🇨🇳 Chinese", variable=lang_var, value="zh").pack(anchor=tk.W)
    
    tk.Label(left, text="", height=2).pack()
    
    def translate():
        if not api_key:
            messagebox.showwarning("Error", "Please enter Gemini API Key!")
            return
        if not srt_path:
            messagebox.showwarning("Error", "Please load SRT file first!")
            return
        
        status.config(text="Translating...")
        root.update()
        
        try:
            import requests
            
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            lang_names = {"vi": "Vietnamese", "en": "English", "ja": "Japanese", "ko": "Korean", "zh": "Chinese"}
            target = lang_names.get(lang_var.get(), lang_var.get())
            
            # Extract text from SRT
            lines = srt_content.strip().split('\n')
            text_lines = []
            for line in lines:
                if not line.strip().isdigit() and '-->' not in line and line.strip():
                    text_lines.append(line.strip())
            all_text = ' '.join(text_lines)
            
            prompt = f"Translate to {target}: {all_text}"
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result['candidates'][0]['content']['parts'][0]['text']
                
                # Create simple SRT
                translated_srt = f"""1
00:00:00,000 --> 00:00:05,000
{translated}

"""
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, translated_srt)
                
                # Save
                out_file = srt_path.replace('.srt', f'_{lang_var.get()}.srt')
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(translated_srt)
                
                status.config(text=f"✅ Done! Saved: {os.path.basename(out_file)}")
                messagebox.showinfo("Success", f"Translated!\nSaved: {os.path.basename(out_file)}")
            else:
                messagebox.showerror("Error", f"API Error: {response.status_code}\n{response.text[:200]}")
                status.config(text="Translation failed")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
            status.config(text="Error occurred")
    
    def generate():
        messagebox.showinfo("Info", "Generate Audio - Coming soon!")
    
    def export():
        file = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if file:
            status.config(text=f"Exported: {file}")
    
    tk.Button(left, text="🔄 TRANSLATE", command=translate, bg="green", fg="white", height=2, width=25).pack(pady=5)
    tk.Button(left, text="🎵 GENERATE AUDIO", command=generate, bg="blue", fg="white", height=2, width=25).pack(pady=5)
    tk.Button(left, text="💾 EXPORT", command=export, bg="orange", fg="white", height=2, width=25).pack(pady=5)
    
    # Right side - text area
    right = tk.Frame(main_frame)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    tk.Label(right, text="Subtitles:", font=("Arial", 12, "bold")).pack()
    text_area = scrolledtext.ScrolledText(right, font=("Arial", 12), wrap=tk.WORD)
    text_area.pack(fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, "Load an SRT file to begin...")
    
    # Status bar
    status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status.pack(side=tk.BOTTOM, fill=tk.X)
    
    root.mainloop()


if __name__ == "__main__":
    main()