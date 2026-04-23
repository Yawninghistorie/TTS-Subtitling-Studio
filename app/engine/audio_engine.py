"""
Audio Processing Engine
Xử lý, ghép và xuất audio
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
from pathlib import Path
import struct
import wave

try:
    import soundfile as sf

    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import pydub

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioSegment:
    """Một segment audio."""

    def __init__(
        self,
        waveform: np.ndarray,
        sample_rate: int = 22050,
        start_time: float = 0.0,
        end_time: float = None,
    ):
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.start_time = start_time
        self.end_time = end_time if end_time is not None else len(waveform) / sample_rate

    @property
    def duration(self) -> float:
        return len(self.waveform) / self.sample_rate

    @property
    def samples(self) -> int:
        return len(self.waveform)

    def resample(self, target_sr: int) -> "AudioSegment":
        """Resample to target sample rate."""
        if target_sr == self.sample_rate:
            return self

        # Simple linear interpolation resampling
        ratio = target_sr / self.sample_rate
        new_length = int(len(self.waveform) * ratio)
        indices = np.linspace(0, len(self.waveform) - 1, new_length)
        resampled = np.interp(indices, np.arange(len(self.waveform)), self.waveform)

        return AudioSegment(
            waveform=resampled.astype(np.float32),
            sample_rate=target_sr,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def adjust_speed(self, speed: float) -> "AudioSegment":
        """Adjust playback speed (time-stretch)."""
        if speed == 1.0:
            return self

        # Simple resampling for speed change
        new_length = int(len(self.waveform) / speed)
        indices = np.linspace(0, len(self.waveform) - 1, new_length)
        adjusted = np.interp(indices, np.arange(len(self.waveform)), self.waveform)

        new_end_time = self.start_time + len(adjusted) / self.sample_rate

        return AudioSegment(
            waveform=adjusted.astype(np.float32),
            sample_rate=self.sample_rate,
            start_time=self.start_time,
            end_time=new_end_time,
        )

    def adjust_pitch(self, semitones: float) -> "AudioSegment":
        """Shift pitch by semitones."""
        if semitones == 0.0:
            return self

        # Pitch shift via resampling
        factor = 2 ** (semitones / 12.0)
        new_sr = int(self.sample_rate * factor)
        resampled = self.resample(new_sr)
        resampled.sample_rate = self.sample_rate

        return resampled

    def adjust_volume(self, volume: float) -> "AudioSegment":
        """Adjust volume."""
        return AudioSegment(
            waveform=(self.waveform * volume).astype(np.float32),
            sample_rate=self.sample_rate,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def fade_in(self, duration: float) -> "AudioSegment":
        """Apply fade in."""
        fade_samples = int(duration * self.sample_rate)
        if fade_samples >= len(self.waveform):
            return self

        fade_curve = np.linspace(0, 1, min(fade_samples, len(self.waveform)))
        waveform = self.waveform.copy()
        waveform[: len(fade_curve)] *= fade_curve

        return AudioSegment(
            waveform=waveform,
            sample_rate=self.sample_rate,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def fade_out(self, duration: float) -> "AudioSegment":
        """Apply fade out."""
        fade_samples = int(duration * self.sample_rate)
        if fade_samples >= len(self.waveform):
            return self

        fade_curve = np.linspace(1, 0, min(fade_samples, len(self.waveform)))
        waveform = self.waveform.copy()
        waveform[-len(fade_curve) :] *= fade_curve

        return AudioSegment(
            waveform=waveform,
            sample_rate=self.sample_rate,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def trim(self, start: float, end: float) -> "AudioSegment":
        """Trim segment to start/end time."""
        start_sample = max(0, int(start * self.sample_rate))
        end_sample = min(len(self.waveform), int(end * self.sample_rate))

        return AudioSegment(
            waveform=self.waveform[start_sample:end_sample],
            sample_rate=self.sample_rate,
            start_time=start,
            end_time=end,
        )

    def get_waveform_data(self, target_sr: int = None) -> Tuple[np.ndarray, int]:
        """Get waveform data for visualization."""
        sr = target_sr or self.sample_rate
        if sr != self.sample_rate:
            segment = self.resample(sr)
            return segment.waveform, sr
        return self.waveform, self.sample_rate


class AudioEngine:
    """Audio processing and merging engine."""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.segments: List[AudioSegment] = []

    def add_segment(self, segment: AudioSegment):
        """Add audio segment."""
        self.segments.append(segment)

    def clear(self):
        """Clear all segments."""
        self.segments.clear()

    def merge(
        self,
        crossfade_duration: float = 0.05,
        progress_callback: Callable[[int, int], None] = None,
    ) -> np.ndarray:
        """
        Ghép tất cả segments thành một audio.
        Giữ nguyên timeline của SRT.
        """
        if not self.segments:
            return np.array([], dtype=np.float32)

        # Tìm tổng duration
        total_samples = int(
            max(seg.end_time for seg in self.segments) * self.sample_rate
        )

        # Tạo output buffer
        output = np.zeros(total_samples, dtype=np.float32)
        overlap_masks = np.zeros(total_samples, dtype=np.float32)

        for i, segment in enumerate(self.segments):
            # Convert time to samples
            start_sample = int(segment.start_time * self.sample_rate)
            end_sample = int(segment.end_time * self.sample_rate)

            # Ensure segment fits
            seg_samples = min(len(segment.waveform), end_sample - start_sample)
            if seg_samples <= 0:
                continue

            # Add waveform
            end_idx = min(start_sample + seg_samples, total_samples)
            output[start_sample:end_idx] += segment.waveform[: end_idx - start_sample]
            overlap_masks[start_sample:end_idx] += 1

            if progress_callback:
                progress_callback(i + 1, len(self.segments))

        # Normalize overlapping regions
        valid_mask = overlap_masks > 0
        output[valid_mask] /= overlap_masks[valid_mask]

        return output

    def normalize(self, waveform: np.ndarray, peak_db: float = -3.0) -> np.ndarray:
        """Peak normalize audio."""
        peak = np.max(np.abs(waveform))
        if peak == 0:
            return waveform

        target_peak = 10 ** (peak_db / 20.0)
        return (waveform / peak * target_peak).astype(np.float32)

    def save_wav(self, waveform: np.ndarray, file_path: str):
        """Save as WAV file."""
        if SOUNDFILE_AVAILABLE:
            sf.write(file_path, waveform, self.sample_rate)
        else:
            self._save_wav_simple(waveform, file_path)

    def _save_wav_simple(self, waveform: np.ndarray, file_path: str):
        """Save WAV without soundfile."""
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)

            # Convert to int16
            audio_int = (np.clip(waveform, -1, 1) * 32767).astype(np.int16)
            wav_file.writeframes(audio_int.tobytes())

    def save_mp3(self, waveform: np.ndarray, file_path: str, bitrate: str = "192k"):
        """Save as MP3 (requires ffmpeg)."""
        import subprocess
        import tempfile

        if not PYDUB_AVAILABLE:
            # Fallback: save as WAV
            self.save_wav(waveform, file_path.replace(".mp3", ".wav"))
            return

        # Save to temp WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_wav = tmp.name

        try:
            self.save_wav(waveform, temp_wav)
            sound = pydub.AudioSegment.from_wav(temp_wav)
            sound.export(file_path, format="mp3", bitrate=bitrate)
        finally:
            Path(temp_wav).unlink(missing_ok=True)

    def generate_preview_waveform(
        self, waveform: np.ndarray, num_points: int = 1000
    ) -> List[float]:
        """Generate waveform data for visualization."""
        if len(waveform) <= num_points:
            return waveform.tolist()

        # Downsample
        indices = np.linspace(0, len(waveform) - 1, num_points)
        return np.max(waveform[indices.astype(int) : indices.astype(int) + 100], axis=1).tolist()


class AudioGenerator:
    """Generate audio từ TTS engine."""

    def __init__(self, tts_engine, audio_engine: AudioEngine):
        self.tts_engine = tts_engine
        self.audio_engine = audio_engine

    def generate_from_segments(
        self,
        segments: List[Tuple[str, float, float]],
        speaker_id: int = 0,
        progress_callback: Callable[[int, int], None] = None,
    ) -> np.ndarray:
        """
        Generate audio từ list of (text, start_time, end_time).
        """
        self.audio_engine.clear()
        total = len(segments)

        for i, (text, start_time, end_time) in enumerate(segments):
            # Generate audio from TTS
            waveform = self.tts_engine.infer(text, speaker_id)
            if waveform is None:
                continue

            # Create segment
            duration = end_time - start_time
            segment = AudioSegment(
                waveform=waveform.flatten(),
                sample_rate=self.tts_engine.model_info.sample_rate,
                start_time=start_time,
                end_time=end_time,
            )

            # Resample if needed
            if segment.sample_rate != self.audio_engine.sample_rate:
                segment = segment.resample(self.audio_engine.sample_rate)

            # Trim to fit duration
            max_samples = int(duration * self.audio_engine.sample_rate)
            if segment.samples > max_samples:
                segment.waveform = segment.waveform[:max_samples]
                segment.end_time = start_time + duration

            self.audio_engine.add_segment(segment)

            if progress_callback:
                progress_callback(i + 1, total)

        return self.audio_engine.merge()