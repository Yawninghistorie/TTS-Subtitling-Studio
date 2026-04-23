# TTS Subtitling Studio — Specification

## 1. Project Overview

**Name:** TTS Subtitling Studio (TTS-Sub)
**Type:** Desktop Application (Windows .exe)
**Core Function:** Drag & drop SRT → Gemini translate → ONNX TTS → Audio file
**Target:** Content creators, translators, video producers

## 2. Core Features

### 2.1 File I/O
- [x] Drag & drop zone cho file SRT, file ONNX model, file ONNX.json config
- [x] Hỗ trợ nhiều file SRT cùng lúc (tự động ghép theo thứ tự thời gian)
- [x] Load model TTS: tự động nhận diện .onnx + .onnx.json trong cùng folder
- [x] Preview wave form trước khi generate
- [x] Xuất file: WAV (mặc định), MP3 (ffmpeg)

### 2.2 Model Management
- [x] Auto-detect TTS model (cần .onnx + .onnx.json cùng folder)
- [x] Hiển thị thông tin model: sample rate, languages, speakers
- [x] Preview giọng nói với text mẫu
- [x] Chọn speaker/voice ID nếu model hỗ trợ multi-speaker

### 2.3 SRT Processing
- [x] Parse SRT: index, start/end time, text
- [x] Validate timing (end > start, no overlap nghiêm trọng)
- [x] Gộp các entry liền kề cùng speaker để TTS tự nhiên hơn
- [x] Split lại nếu entry quá dài (> threshold theo model)

### 2.4 Translation Engine (Gemini)
- [x] Dịch toàn bộ SRT text bằng Gemini (context preservation)
- [x] Language detection tự động
- [x] Chọn ngôn ngữ đích (dropdown)
- [x] Preserve timing nguyên bản
- [x] Batch translate: chia nhỏ nếu file quá lớn
- [x] Cache translated text (tránh re-translate khi chỉnh sửa nhẹ)

### 2.5 TTS Generation
- [x] Batch inference: xử lý từng chunk để tránh OOM
- [x] Speaker embedding support
- [x] Smooth crossfade giữa các segment
- [x] Progress bar với ETA

### 2.6 Audio Post-processing
- [x] Merge segments theo timeline SRT
- [x] Normalize volume (peak normalization)
- [x] Fade in/out cho đầu/cuối
- [x] Preview kết quả trước khi export
- [x] Export WAV (uncompressed) hoặc MP3

### 2.7 Subtitle Editor (Live Edit)
- [x] Hiển thị danh sách subtitles dạng bảng
- [x] Edit trực tiếp: text, start time, end time
- [x] Preview segment riêng lẻ
- [x] Undo/Redo
- [x] Search & Replace
- [x] Insert/Delete entry
- [x] Highlight overlap timing

### 2.8 Additional Polish Features
- [x] Timeline visualization với waveform preview
- [x] Speed adjustment per segment
- [x] Pitch shift per segment
- [x] Volume adjustment per segment
- [x] Batch process nhiều SRT cùng lúc
- [x] Dark/Light theme toggle
- [x] Keyboard shortcuts

## 3. UI Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [Logo] TTS Subtitling Studio          [Theme] [Settings] [About]      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────┐  ┌────────────────────────────────────────┐ │
│  │  DROP ZONE           │  │  MODEL INFO PANEL                       │ │
│  │  ┌────────────────┐  │  │  - Name: xtts_v2.0                     │ │
│  │  │  📁 Drop files │  │  │  - Sample Rate: 22050 Hz               │ │
│  │  │  here...       │  │  │  - Languages: en, vi, es...            │ │
│  │  └────────────────┘  │  │  - Speakers: 3 voices                  │ │
│  │                      │  │  Speaker: [▼ Dropdown] [▶ Preview]    │ │
│  │  Model: [folder]      │  │                                        │ │
│  │  SRT: [list]          │  └────────────────────────────────────────┘ │
│  │                      │                                              │
│  │  Target Lang: [▼ VN]  │  ┌────────────────────────────────────────┐ │
│  │  [🔄 Translate]      │  │  WAVEFORM / TIMELINE PREVIEW            │ │
│  └──────────────────────┘  └────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  SUBTITLE EDITOR                                                  │  │
│  │  ┌────┬──────────┬──────────┬──────────────────┬───────┬─────────┐│  │
│  │  │ #  │ Start   │ End      │ Text              │ Dur   │ Actions ││  │
│  │  ├────┼──────────┼──────────┼──────────────────┼───────┼─────────┤│  │
│  │  │ 1  │ 00:00:00│ 00:00:03 │ Hello everyone   │ 3.0s  │ [▶][✏][🗑]││  │
│  │  │ 2  │ 00:00:03│ 00:00:05 │ Welcome to...    │ 2.0s  │ [▶][✏][🗑]││  │
│  │  │ 3  │ 00:00:05│ 00:00:08 │ Today we will...  │ 3.0s  │ [▶][✏][🗑]││  │
│  │  └────┴──────────┴──────────┴──────────────────┴───────┴─────────┘│  │
│  │  [+ Insert] [Delete Selected] [Undo] [Redo] [🔍 Search]           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AUDIO SETTINGS              │  AUDIO SETTINGS                      │  │
│  │  Volume: [────●────] 100%   │  Fade In: [──●────] 0.1s            │  │
│  │  Speed:  [────●────] 1.0x   │  Fade Out:[──●────] 0.2s            │  │
│  │  Pitch:  [────●────] 0 sem  │  Normalize: [✓] Peak: -3dB          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  [▶ Generate Audio]  [▶▶ Generate All]  Progress: [████████░░] 80%    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4. Technical Stack

- **Frontend:** Flet (Flutter-based Python UI)
- **TTS:** ONNX Runtime
- **Translation:** Gemini API (google-genai SDK)
- **Audio:** pydub, soundfile, numpy
- **Packaging:** PyInstaller
- **Build target:** Windows .exe (standalone)

## 5. File Formats

### 5.1 SRT Format
```
1
00:00:00,000 --> 00:00:03,500
Hello everyone

2
00:00:03,500 --> 00:00:05,000
Welcome to the show
```

### 5.2 ONNX Model Config (.onnx.json)
```json
{
  "model_name": "xtts_v2.0",
  "sample_rate": 22050,
  "languages": ["en", "vi", "es"],
  "speakers": [
    {"id": 0, "name": "Female 1"},
    {"id": 1, "name": "Male 1"},
    {"id": 2, "name": "Female 2"}
  ],
  "input_sr": 24000,
  "mel_channels": 80,
  "vocab_size": 123
}
```

## 6. Edge Cases

- [x] Empty SRT file → warn & skip
- [x] Missing ONNX config → use defaults
- [x] Unsupported language → show error, allow fallback to source lang
- [x] Gemini API failure → retry 3x, then show error
- [x] OOM on large file → batch processing
- [x] Overlap timing → warn, don't auto-fix (user decision)
- [x] Segment too long → auto-split with pause at middle
- [x] No internet → cached translation + offline mode

## 7. Keyboard Shortcuts

| Shortcut       | Action              |
|---------------|---------------------|
| Ctrl+O        | Open file           |
| Ctrl+S        | Save                |
| Ctrl+Z        | Undo                |
| Ctrl+Y        | Redo                |
| Ctrl+F        | Find                |
| Ctrl+Enter    | Preview segment    |
| F5            | Generate all        |
| Space         | Play/Pause preview  |
| Ctrl+T        | Translate           |
| Delete        | Delete selected     |
| Ctrl+N        | New subtitle entry  |
| Escape        | Cancel edit         |