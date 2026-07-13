from pathlib import Path
def load_theme():
    p=Path(__file__).resolve().parents[1]/'resources'/'app.qss'
    return p.read_text(encoding='utf-8') if p.exists() else ''
