# TTS Subtitling Studio Build Script

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def main():
    """Build the executable."""
    
    # Get paths
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    # Create directories
    dist_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)
    
    # Build arguments
    args = [
        str(project_root / "main.py"),
        f"--name=TTS_Subtitling_Studio",
        f"--onedir",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        f"--specpath={build_dir}",
        "--console=false",
        "--copy-non-parse-assets=resources",
        "--hidden-import=google.genai",
        "--hidden-import=onnxruntime",
        "--hidden-import=flet",
        "--hidden-import=soundfile",
        "--hidden-import=pydub",
    ]
    
    print("Building TTS Subtitling Studio...")
    print(f"Output: {dist_dir / 'TTS_Subtitling_Studio.exe'}")
    
    try:
        PyInstaller.__main__.run(args)
        print("Build complete!")
        print(f"Executable: {dist_dir / 'TTS_Subtitling_Studio' / 'TTS_Subtitling_Studio.exe'}")
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()