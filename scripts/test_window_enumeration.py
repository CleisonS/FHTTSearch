from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.window_service import WindowService  # noqa: E402


def main() -> int:
    try:
        windows = WindowService().list_windows()
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    for window in windows:
        print(f"HWND={window.handle}")
        print(f"PID={window.pid}")
        print(f"Processo={window.process_name}")
        print(f"Classe={window.class_name}")
        print(f"Visível={window.visible}")
        print(f"Título={window.title}")
        print("-" * 60)
    print(f"Total={len(windows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
