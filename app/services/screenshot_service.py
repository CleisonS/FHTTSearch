from __future__ import annotations

from pathlib import Path

from PIL import ImageGrab

from app.utils.file_utils import ensure_dir, sanitize_filename, timestamp


class ScreenshotService:
    def __init__(self, directory: Path = Path("output/screenshots")) -> None:
        self.directory = ensure_dir(directory)

    def capture_desktop(self) -> Path:
        path = self.directory / f"{timestamp()}_desktop.png"
        ImageGrab.grab(all_screens=True).save(path)
        return path

    def capture_region(self, rect: dict, title: str = "control") -> Path:
        left = int(rect.get("left", 0))
        top = int(rect.get("top", 0))
        right = int(rect.get("right", 0))
        bottom = int(rect.get("bottom", 0))
        if right <= left or bottom <= top:
            raise ValueError(f"Retângulo inválido para screenshot: {rect}")
        path = self.directory / f"{timestamp()}_control_{sanitize_filename(title)}.png"
        ImageGrab.grab(bbox=(left, top, right, bottom)).save(path)
        return path

    def capture_window(self, window) -> Path:
        if getattr(window, "minimized", False):
            raise ValueError("A janela selecionada está minimizada; restaure-a antes de capturar.")
        return self.capture_region(window.rectangle, window.title or "window")
