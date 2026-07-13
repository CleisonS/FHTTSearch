from __future__ import annotations
from pathlib import Path
from PIL import ImageGrab
from app.utils.file_utils import ensure_dir, sanitize_filename, timestamp
class ScreenshotService:
    def __init__(self, directory:Path=Path('output/screenshots')): self.directory=ensure_dir(directory)
    def capture_desktop(self):
        p=self.directory/f"{timestamp()}_desktop.png"; ImageGrab.grab(all_screens=True).save(p); return p
    def capture_region(self, rect:dict, title='control'):
        p=self.directory/f"{timestamp()}_control_{sanitize_filename(title)}.png"; ImageGrab.grab(bbox=(rect['left'],rect['top'],rect['right'],rect['bottom'])).save(p); return p
    def capture_window(self, window): return self.capture_region(window.rectangle, window.title or 'window')
