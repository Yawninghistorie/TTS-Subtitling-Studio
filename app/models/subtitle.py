"""
Subtitle Data Model
"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional, List
from enum import Enum


class SubtitleState(Enum):
    ORIGINAL = "original"
    TRANSLATED = "translated"
    GENERATED = "generated"
    ERROR = "error"


@dataclass
class SubtitleEntry:
    """Một entry phụ đề."""

    index: int
    start_time: timedelta
    end_time: timedelta
    text: str
    state: SubtitleState = SubtitleState.ORIGINAL
    translated_text: Optional[str] = None
    audio_path: Optional[str] = None
    speed: float = 1.0
    pitch: float = 0.0  # semitones
    volume: float = 1.0
    error_message: Optional[str] = None

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @property
    def duration_seconds(self) -> float:
        return self.duration.total_seconds()

    @property
    def display_text(self) -> str:
        return self.translated_text or self.text

    def is_valid(self) -> bool:
        return self.end_time > self.start_time and len(self.text.strip()) > 0

    def overlaps(self, other: "SubtitleEntry") -> bool:
        return self.start_time < other.end_time and self.end_time > other.start_time

    def format_srt_time(self, td: timedelta) -> str:
        """Format timedelta to SRT time format: HH:MM:SS,mmm"""
        total_ms = int(td.total_seconds() * 1000)
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        millis = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    def to_srt_line(self) -> str:
        """Convert to SRT format line."""
        text = self.display_text
        return f"{self.index}\n{self.format_srt_time(self.start_time)} --> {self.format_srt_time(self.end_time)}\n{text}\n"

    @classmethod
    def from_srt_block(cls, block: str, index: int) -> "SubtitleEntry":
        """Parse SRT block string to SubtitleEntry."""
        lines = block.strip().split("\n")
        if len(lines) < 3:
            raise ValueError(f"Invalid SRT block at index {index}")

        # Parse timing line
        timing = lines[1]
        if "-->" not in timing:
            raise ValueError(f"Invalid timing at index {index}")

        start_str, end_str = timing.split("-->")
        start = cls._parse_srt_time(start_str.strip())
        end = cls._parse_srt_time(end_str.strip())

        # Text is everything after timing line
        text = "\n".join(lines[2:])

        return cls(index=index, start_time=start, end_time=end, text=text)

    @staticmethod
    def _parse_srt_time(time_str: str) -> timedelta:
        """Parse SRT time string to timedelta."""
        # Format: HH:MM:SS,mmm or HH:MM:SS.mmm
        time_str = time_str.replace(",", ".")
        parts = time_str.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid time format: {time_str}")

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split(".")
        seconds = int(seconds_parts[0])
        millis = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

        return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=millis)


@dataclass
class SubtitleFile:
    """Tập tin phụ đề với nhiều entries."""

    entries: List[SubtitleEntry] = field(default_factory=list)
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    file_path: Optional[str] = None

    @classmethod
    def from_srt_file(cls, file_path: str) -> "SubtitleFile":
        """Load SubtitleFile from SRT file path."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return cls.from_srt_content(content, file_path)

    @classmethod
    def from_srt_content(cls, content: str, file_path: str = None) -> "SubtitleFile":
        """Parse SRT content string to SubtitleFile."""
        blocks = content.strip().split("\n\n")
        entries = []
        for i, block in enumerate(blocks):
            if block.strip():
                try:
                    entry = SubtitleEntry.from_srt_block(block, i + 1)
                    if entry.is_valid():
                        entries.append(entry)
                except ValueError as e:
                    print(f"Warning: Skipping invalid block {i + 1}: {e}")

        return cls(entries=entries, file_path=file_path)

    def save(self, file_path: str = None):
        """Save to SRT file."""
        path = file_path or self.file_path
        if not path:
            raise ValueError("No file path specified")

        with open(path, "w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(entry.to_srt_line() + "\n")

        self.file_path = path

    def total_duration(self) -> timedelta:
        """Total duration of all entries."""
        if not self.entries:
            return timedelta(0)
        return self.entries[-1].end_time

    def get_text_concat(self) -> str:
        """Concatenate all text for translation."""
        return " ".join(e.display_text for e in self.entries)

    def detect_language(self) -> str:
        """Simple language detection."""
        sample = " ".join(e.text[:50] for e in self.entries[:5])
        # Simple heuristic - check for Vietnamese characters
        if any(c in sample for c in "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"):
            return "vi"
        # Check for Chinese characters
        if any("\u4e00" <= c <= "\u9fff" for c in sample):
            return "zh"
        # Check for Japanese
        if any(c in sample for c in "ぁ-んァ-ン\u3000-\u303f"):
            return "ja"
        # Check for Korean
        if any("\uac00" <= c <= "\ud7af" for c in sample):
            return "ko"
        # Check for Arabic
        if any("\u0600" <= c <= "\u06ff" for c in sample):
            return "ar"
        return "en"  # Default to English

    def merge_adjacent(self, gap_threshold: float = 0.5):
        """Merge entries that are close together."""
        if not self.entries:
            return

        merged = [self.entries[0]]
        for entry in self.entries[1:]:
            last = merged[-1]
            gap = (entry.start_time - last.end_time).total_seconds()
            if gap <= gap_threshold:
                # Extend last entry to cover this one
                last.end_time = entry.end_time
                last.text += " " + entry.text
                if last.translated_text and entry.translated_text:
                    last.translated_text += " " + entry.translated_text
            else:
                merged.append(entry)

        self.entries = merged
        # Re-index
        for i, entry in enumerate(self.entries):
            entry.index = i + 1

    def split_long_entries(self, max_chars: int = 200):
        """Split entries that are too long."""
        new_entries = []
        for entry in self.entries:
            if len(entry.text) <= max_chars:
                new_entries.append(entry)
            else:
                # Split by sentences
                sentences = entry.text.split(". ")
                current_text = ""
                current_start = entry.start_time
                avg_char_duration = entry.duration_seconds / max(len(entry.text), 1) * max_chars

                for sentence in sentences:
                    if len(current_text) + len(sentence) <= max_chars:
                        current_text += sentence + ". "
                    else:
                        if current_text:
                            new_entries.append(
                                SubtitleEntry(
                                    index=len(new_entries) + 1,
                                    start_time=current_start,
                                    end_time=current_start + timedelta(seconds=avg_char_duration / 5),
                                    text=current_text.strip(),
                                )
                            )
                            current_start = new_entries[-1].end_time
                        current_text = sentence + ". "

                if current_text:
                    new_entries.append(
                        SubtitleEntry(
                            index=len(new_entries) + 1,
                            start_time=current_start,
                            end_time=entry.end_time,
                            text=current_text.strip(),
                        )
                    )

        self.entries = new_entries

    def to_dict_list(self) -> List[dict]:
        """Convert to list of dicts for UI."""
        return [
            {
                "index": e.index,
                "start": e.format_srt_time(e.start_time),
                "end": e.format_srt_time(e.end_time),
                "text": e.text,
                "translated": e.translated_text or "",
                "state": e.state.value,
            }
            for e in self.entries
        ]