# 🎬 TTS Subtitling Studio

**Ứng dụng Desktop chuyển phụ đề SRT sang âm thanh với TTS + Dịch thuật Gemini**

> 📌 Chuyển file `.srt` thành âm thanh chất lượng cao bằng model TTS ONNX, với tính năng dịch thuật chuẩn xác bằng Gemini AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-purple)

---

## ✨ Tính năng chính

### 📁 Xử lý File
- **Drag & Drop** - Kéo thả file SRT và model TTS trực tiếp
- **Đa file SRT** - Hỗ trợ nhiều file cùng lúc, tự động ghép theo timeline
- **Auto-detect Model** - Tự động nhận diện model TTS từ folder `.onnx` + `.onnx.json`

### 🌐 Dịch thuật Gemini
- **Context Preservation** - Dịch toàn bộ nội dung để đảm bảo tính nhất quán
- **20+ ngôn ngữ** - Hỗ trợ tiếng Việt, Anh, Nhật, Hàn, Trung, Pháp, Đức...
- **Colloquial Translation** - Giữ nguyên slang, tiếng lóng tự nhiên
- **Translation Cache** - Không re-dịch khi chỉnh sửa nhẹ

### 🎙️ Model TTS ONNX
- **ONNX Runtime** - Inference nhanh, cross-platform
- **Multi-Speaker** - Hỗ trợ nhiều giọng đọc
- **Batch Processing** - Xử lý hàng loạt tránh OOM
- **Preview Voice** - Nghe thử trước khi generate

### 🎚️ Chỉnh sửa âm thanh
- **Volume** - Điều chỉnh âm lượng (0-200%)
- **Speed** - Thay đổi tốc độ (0.5x - 2x)
- **Pitch** - Shift cao độ theo semitone (-12 to +12)
- **Fade In/Out** - Hiệu ứng mở đầu/kết thúc
- **Normalize** - Cân bằng âm lượng peak

### ✏️ Editor phụ đề trực tiếp
- **Live Edit** - Chỉnh sửa text trực tiếp trên bảng
- **Edit timing** - Sửa start/end time riêng lẻ
- **Insert/Delete** - Thêm hoặc xóa entry
- **Undo/Redo** - Quay lại/thực hiện lại thao tác
- **Search** - Tìm kiếm nhanh trong subtitles

---

## 🚀 Cách sử dụng

### Bước 1: Khởi động ứng dụng

```bash
# Windows
dist\TTS_Subtitling_Studio.exe

# Hoặc chạy Python trực tiếp
python main.py
```

### Bước 2: Load Model TTS

**Cách 1:** Kéo thả folder chứa file `.onnx` + `.onnx.json` vào drop zone

**Cách 2:** Click icon folder trong "Model Path" → Chọn folder chứa model

**File cấu hình model (`.onnx.json`):**
```json
{
  "model_name": "xtts_v2.0",
  "sample_rate": 22050,
  "languages": ["en", "vi", "es"],
  "speakers": [
    {"id": 0, "name": "Female 1"},
    {"id": 1, "name": "Male 1"}
  ]
}
```

### Bước 3: Load File SRT

**Kéo thả** file `.srt` vào drop zone

Hoặc click vào drop zone → Chọn file

### Bước 4: Chọn ngôn ngữ đích

Chọn ngôn ngữ mong muốn từ dropdown:
- 🇻🇳 Tiếng Việt
- 🇺🇸 English  
- 🇯🇵 日本語
- 🇰🇷 한국어
- 🇨🇳 中文
- 🇫🇷 Français
- ...

### Bước 5: Dịch thuật (Optional)

Click **Translate** để dịch toàn bộ subtitles

> ⚠️ **Cần Gemini API Key**: Đặt biến môi trường `GEMINI_API_KEY`

### Bước 6: Chỉnh sửa (Optional)

Trong bảng **Subtitle Editor**:
- Double-click entry để sửa text/timing
- Dùng toolbar để insert/delete
- Preview từng entry riêng lẻ

### Bước 7: Generate Audio

Điều chỉnh **Audio Settings**:
- Volume, Speed, Pitch
- Fade In/Out
- Normalize level

Click **Generate Audio** để tạo âm thanh

### Bước 8: Export

Click **Export** để lưu file:
- `.wav` - Uncompressed (mặc định)
- `.mp3` - Compressed (cần ffmpeg)

---

## ⌨️ Keyboard Shortcuts

| Phím | Chức năng |
|------|-----------|
| `Ctrl+O` | Mở file |
| `Ctrl+S` | Lưu file |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+F` | Tìm kiếm |
| `Ctrl+N` | Thêm entry mới |
| `Delete` | Xóa entry |
| `F5` | Generate all |
| `Space` | Play/Pause preview |

---

## 📂 Cấu trúc Project

```
TTS_Subtitling_Studio/
├── main.py                 # Entry point
├── app/
│   ├── models/
│   │   └── subtitle.py   # Data models
│   ├── engine/
│   │   ├── srt_parser.py        # SRT parser
│   │   ├── tts_engine.py       # ONNX TTS engine
│   │   ├── translation_engine.py # Gemini translator
│   │   └── audio_engine.py    # Audio processing
│   └── ui/
│       ├── main_page.py        # Main UI
│       ├── drop_zone.py       # File drop zone
│       ├── model_panel.py     # Model info
│       ├── subtitle_editor.py # Subtitle editing
│       ├── audio_controls.py  # Audio settings
│       └── waveform_display.py # Waveform preview
├── dist/
│   └── TTS_Subtitling_Studio  # ✅ Executable
├── requirements.txt
└── SPEC.md                  # Full specifications
```

---

## 🔧 Requirements

### Python Dependencies

```
flet>=0.25.0          # UI framework
onnxruntime>=1.18.0     # ONNX inference
soundfile>=0.12.0        # Audio I/O
pydub>=0.25.0           # Audio processing
google-genai>=0.8.0    # Gemini API
numpy>=1.24.0           # Array processing
```

### System Requirements

- **OS**: Windows 10+ (built executable)
- **Python**: 3.10+ (development)
- **RAM**: 4GB+ recommended
- **Disk**: 100MB free space

### Optional

- **ffmpeg**: For MP3 export
- **GPU**: CUDA-capable GPU for faster TTS (optional)

---

## ⚙️ Configuration

### Environment Variables

```bash
# Gemini API Key (required for translation)
export GEMINI_API_KEY="your-api-key-here"

# Output directory (optional)
export OUTPUT_DIR="/path/to/output"
```

### Settings Dialog

Click icon ⚙️ trong header để:
- Nhập Gemini API Key
- Chọn output directory
- Thay đổi theme

---

## 🎨 UI Theme

Ứng dụng hỗ trợ **Dark** và **Light** mode.

Click icon 🌙/☀️ trong header để toggle.

---

## 🔮 Supported Languages (Gemini)

| Code | Language | Tiếng Việt |
|------|---------|------------|
| en | English | Tiếng Anh |
| vi | Vietnamese | Tiếng Việt |
| ja | Japanese | Tiếng Nhật |
| ko | Korean | Tiếng Hàn |
| zh | Chinese | Tiếng Trung |
| fr | French | Tiếng Pháp |
| de | German | Tiếng Đức |
| es | Spanish | Tiếng Tây Ban Nha |
| it | Italian | Tiếng Ý |
| pt | Portuguese | Tiếng Bồ Đào Nha |
| ru | Russian | Tiếng Nga |
| ar | Arabic | Tiếng Ả Rập |
| hi | Hindi | Tiếng Hindi |
| th | Thai | Tiếng Thái |
| id | Indonesian | Tiếng Indonesia |
| nl | Dutch | Tiếng Hà Lan |
| pl | Polish | Tiếng Ba Lan |
| tr | Turkish | Tiếng Thổ Nhĩ Kỳ |

---

## 🐛 Troubleshooting

### Lỗi thường gặp

**Q: "ONNX model not loading"**
```
A: Đảm bảo file .onnx và .onnx.json cùng folder
```

**Q: "Translation failed"**
```
A: Kiểm tra GEMINI_API_KEY đã được đặt chưa
```

**Q: "Audio too loud/quiet"**
```
A: Adjust Volume slider hoặc enable Normalize
```

**Q: "Out of memory"**
```
A: Xử lý file nhỏ hơn hoặc tăng RAM
```

---

## 🤝 Contributing

Pull requests welcome!

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open PR

---

## 📜 License

MIT License - Xem LICENSE file

---

## 🙏 Credits

- **Flet** - Modern Python UI framework
- **ONNX Runtime** - Cross-platform ML inference
- **Google Gemini** - AI translation
- **PyInstaller** - Executable packaging

---

## 📞 Contact

- **Author**: TTS Studio Team
- **Version**: 1.0.0
- **Issues**: GitHub Issues

---

**Made with ❤️ for content creators**

```
╔═══════════════════════════════════════════════════════════╗
║  🎬 TTS Subtitling Studio v1.0.0                       ║
║  SRT → Gemini → ONNX TTS → Audio                       ║
╚═══════════════════════════════════════════════════════════╝
```