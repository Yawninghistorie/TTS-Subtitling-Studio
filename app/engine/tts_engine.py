"""
TTS Model Loader and ONNX Inference Engine
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

try:
    import onnxruntime as ort

    ONNXRUNTIME_AVAILABLE = True
except ImportError:
    ONNXRUNTIME_AVAILABLE = False


@dataclass
class TTSModelInfo:
    """Thông tin model TTS."""

    name: str = "Unknown"
    file_path: str = ""
    sample_rate: int = 22050
    languages: List[str] = None
    speakers: List[Dict[str, Any]] = None
    input_sr: int = 24000
    mel_channels: int = 80
    is_multi_speaker: bool = False
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = ["en"]
        if self.speakers is None:
            self.speakers = [{"id": 0, "name": "default"}]
        if self.config is None:
            self.config = {}

    def __repr__(self):
        return f"TTSModelInfo(name={self.name}, sr={self.sample_rate}, langs={self.languages}, speakers={len(self.speakers)})"


class TTSModelLoader:
    """Loader cho TTS model ONNX."""

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Load .onnx.json config file."""
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def find_models_in_folder(folder_path: str) -> List[str]:
        """Tìm tất cả file .onnx trong folder."""
        folder = Path(folder_path)
        if not folder.exists():
            return []

        models = []
        for onnx_file in folder.glob("*.onnx"):
            # Check if corresponding .onnx.json exists
            json_path = onnx_file.with_suffix(".onnx.json")
            if json_path.exists():
                models.append(str(onnx_file))
            else:
                # Still include if there's any .onnx.json in folder
                json_files = list(folder.glob("*.onnx.json"))
                if json_files:
                    models.append(str(onnx_file))

        return models

    @classmethod
    def load_model(cls, model_path: str) -> Optional[TTSModelInfo]:
        """Load TTS model info từ model path."""
        if not ONNXRUNTIME_AVAILABLE:
            print("Warning: onnxruntime not available")
            return None

        model_path = Path(model_path)
        if not model_path.exists():
            return None

        config_path = model_path.with_suffix(".onnx.json")
        if config_path.exists():
            config = cls.load_config(str(config_path))
        else:
            config = {}

        languages = config.get("languages", ["en"])
        speakers = config.get("speakers", [{"id": 0, "name": "default"}])

        return TTSModelInfo(
            name=model_path.stem,
            file_path=str(model_path),
            sample_rate=config.get("sample_rate", 22050),
            languages=languages,
            speakers=speakers,
            input_sr=config.get("input_sr", 24000),
            mel_channels=config.get("mel_channels", 80),
            is_multi_speaker=len(speakers) > 1,
            config=config,
        )


class TTSEngine:
    """
    Inference engine cho TTS ONNX model.
    Hỗ trợ các loại model TTS phổ biến.
    """

    def __init__(self, model_info: TTSModelInfo):
        self.model_info = model_info
        self.session = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize ONNX Runtime session."""
        if not ONNXRUNTIME_AVAILABLE:
            return False

        try:
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(
                self.model_info.file_path,
                sess_options=sess_options,
                providers=["CPUExecutionProvider"],
            )
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize ONNX model: {e}")
            return False

    def get_input_names(self) -> List[str]:
        """Get model input names."""
        if not self._initialized:
            return []
        return [inp.name for inp in self.session.get_inputs()]

    def get_output_names(self) -> List[str]:
        """Get model output names."""
        if not self._initialized:
            return []
        return [out.name for out in self.session.get_outputs()]

    def infer(self, text: str, speaker_id: int = 0) -> Optional[np.ndarray]:
        """
        Chạy inference cho một đoạn text.
        Trả về audio waveform as numpy array.
        """
        if not self._initialized:
            return None

        try:
            # This is a generic interface - specific models may need different inputs
            inputs = self._prepare_inputs(text, speaker_id)
            outputs = self.session.run(None, inputs)
            return outputs[0] if outputs else None
        except Exception as e:
            print(f"Inference error: {e}")
            return None

    def _prepare_inputs(self, text: str, speaker_id: int) -> Dict[str, Any]:
        """Prepare inputs cho model."""
        # Generic - specific TTS models may have different input schemas
        input_names = self.get_input_names()
        inputs = {}

        if "text" in input_names:
            inputs["text"] = np.array([text], dtype=np.object_)
        if "text_lengths" in input_names:
            inputs["text_lengths"] = np.array([len(text)], dtype=np.int64)
        if "speaker_id" in input_names:
            inputs["speaker_id"] = np.array([speaker_id], dtype=np.int64)
        if "speaker_embedding" in input_names:
            # Placeholder speaker embedding
            inputs["speaker_embedding"] = np.zeros((1, 512), dtype=np.float32)

        return inputs

    def generate_batch(
        self, texts: List[str], speaker_id: int = 0, progress_callback=None
    ) -> List[Optional[np.ndarray]]:
        """Generate audio cho nhiều texts."""
        results = []
        for i, text in enumerate(texts):
            audio = self.infer(text, speaker_id)
            results.append(audio)
            if progress_callback:
                progress_callback(i + 1, len(texts))

        return results

    def supported_languages(self) -> List[str]:
        """Get supported languages."""
        return self.model_info.languages

    def is_language_supported(self, lang: str) -> bool:
        """Check if language is supported."""
        return lang in self.model_info.languages or "*" in self.model_info.languages