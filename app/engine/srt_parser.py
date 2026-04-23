"""
SRT Parser - Parse and validate SRT subtitle files
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from app.models.subtitle import SubtitleFile, SubtitleEntry
from datetime import timedelta


class SRTParser:
    """Parser for SRT subtitle files."""

    # Regex for SRT time format: HH:MM:SS,mmm or HH:MM:SS.mmm
    TIME_PATTERN = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
    )

    @classmethod
    def parse_time(cls, time_str: str) -> timedelta:
        """Parse SRT time string to timedelta."""
        match = cls.TIME_PATTERN.match(time_str.strip())
        if not match:
            raise ValueError(f"Invalid time format: {time_str}")

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        millis = int(match.group(4))

        return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=millis)

    @classmethod
    def format_time(cls, td: timedelta) -> str:
        """Format timedelta to SRT time string."""
        total_ms = int(td.total_seconds() * 1000)
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        millis = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    @classmethod
    def parse_file(cls, file_path: str) -> SubtitleFile:
        """Parse SRT file to SubtitleFile."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return cls.parse_content(content, file_path)

    @classmethod
    def parse_content(cls, content: str, file_path: str = None) -> SubtitleFile:
        """Parse SRT content string."""
        # Normalize line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        blocks = content.strip().split("\n\n")

        entries = []
        for i, block in enumerate(blocks):
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n")
            if len(lines) < 3:
                continue

            # Parse index
            try:
                index = int(lines[0].strip())
            except ValueError:
                continue

            # Parse timing
            timing_match = cls.TIME_PATTERN.search(lines[1])
            if not timing_match:
                continue

            start_str = lines[1][: timing_match.end()].split("-->")[0].strip()
            end_str = lines[1][: timing_match.end()].split("-->")[1].strip()

            try:
                start_time = cls.parse_time(start_str)
                end_time = cls.parse_time(end_str)
            except ValueError:
                continue

            # Parse text (may span multiple lines)
            text = "\n".join(lines[2:])

            if not text.strip():
                continue

            entries.append(
                SubtitleEntry(index=index, start_time=start_time, end_time=end_time, text=text)
            )

        sub_file = SubtitleFile(entries=entries, file_path=file_path)
        sub_file.source_lang = sub_file.detect_language()
        return sub_file

    @classmethod
    def save_file(cls, sub_file: SubtitleFile, file_path: str = None):
        """Save SubtitleFile to SRT file."""
        path = file_path or sub_file.file_path
        if not path:
            raise ValueError("No file path specified")

        lines = []
        for entry in sub_file.entries:
            text = entry.translated_text if entry.translated_text else entry.text
            start = cls.format_time(entry.start_time)
            end = cls.format_time(entry.end_time)
            lines.append(f"{entry.index}\n{start} --> {end}\n{text}\n")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(lines) + "\n")

    @classmethod
    def validate_timing(cls, sub_file: SubtitleFile) -> List[Tuple[int, str]]:
        """Validate timing and return list of warnings."""
        warnings = []

        for i, entry in enumerate(sub_file.entries):
            # Check if end > start
            if entry.end_time <= entry.start_time:
                warnings.append((entry.index, f"Entry {entry.index}: End time must be after start time"))

            # Check if duration is too short
            if entry.duration_seconds < 0.3:
                warnings.append((entry.index, f"Entry {entry.index}: Duration too short (< 0.3s)"))

            # Check if duration is too long
            if entry.duration_seconds > 30:
                warnings.append((entry.index, f"Entry {entry.index}: Duration too long (> 30s)"))

            # Check for overlap with next entry
            if i < len(sub_file.entries) - 1:
                next_entry = sub_file.entries[i + 1]
                if entry.end_time > next_entry.start_time:
                    overlap = (entry.end_time - next_entry.start_time).total_seconds()
                    warnings.append(
                        (
                            entry.index,
                            f"Entry {entry.index}: Overlaps with entry {next_entry.index} by {overlap:.2f}s",
                        )
                    )

        return warnings

    @classmethod
    def sort_entries(cls, sub_file: SubtitleFile, by: str = "time"):
        """Sort entries by time or index."""
        if by == "time":
            sub_file.entries.sort(key=lambda e: e.start_time)
        elif by == "index":
            sub_file.entries.sort(key=lambda e: e.index)

        # Re-index
        for i, entry in enumerate(sub_file.entries):
            entry.index = i + 1