from __future__ import annotations
import csv, json
from pathlib import Path
from app.utils.serialization import to_plain
from app.utils.file_utils import ensure_dir
class ExportService:
    control_columns = ['index','parent_index','depth','backend','name','text','control_type','friendly_class_name','class_name','automation_id','handle','process_id','left','top','right','bottom','width','height','enabled','visible','focused','keyboard_focusable','offscreen','children_count','error']
    def export_json(self, data, path: Path):
        ensure_dir(path.parent); path.write_text(json.dumps(to_plain(data), ensure_ascii=False, indent=2), encoding='utf-8'); return path
    def export_txt(self, inspection, path: Path):
        ensure_dir(path.parent)
        lines = ['UNM Inspector - Relatório', 'AUTOMATION READINESS', json.dumps(to_plain(getattr(inspection, 'readiness', {})), ensure_ascii=False, indent=2)]
        for label, controls in [('WIN32', getattr(inspection, 'controls_win32', [])), ('UIA', getattr(inspection, 'controls_uia', []))]:
            lines.append(f"\nCONTROLES {label}")
            for c in controls:
                lines.append('    ' * c.depth + f'[{c.index}] {c.control_type} Name={c.name} Class={c.class_name} Backend={c.backend}')
        path.write_text('\n'.join(lines), encoding='utf-8'); return path
    def export_controls_csv(self, controls, path: Path, delimiter=';'):
        ensure_dir(path.parent)
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.control_columns, delimiter=delimiter); writer.writeheader()
            for c in controls:
                d = to_plain(c); rect = d.get('rectangle') or {}; d.update(rect); d['width'] = c.width; d['height'] = c.height; d['error'] = ' | '.join(c.errors)
                writer.writerow({k: d.get(k, '') for k in self.control_columns})
        return path
    def export_windows_csv(self, windows, path: Path, delimiter=';'):
        ensure_dir(path.parent); cols = ['title','handle','pid','process_name','executable_path','class_name','visible','minimized','maximized']
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=cols, delimiter=delimiter); writer.writeheader()
            for x in windows: writer.writerow({k: to_plain(x).get(k, '') for k in cols})
        return path
    def export_readiness_csv(self, readiness, path: Path, delimiter=';'):
        ensure_dir(path.parent)
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=delimiter); writer.writerow(['item','detected','backend','confidence_score','notes'])
            d = to_plain(readiness)
            for k, v in d.items():
                if isinstance(v, dict) and 'detected' in v:
                    writer.writerow([k, v.get('detected'), v.get('backend'), v.get('confidence_score'), ' | '.join(v.get('notes', []))])
            writer.writerow(['classification', True, '', d.get('confidence_score'), d.get('classification')])
        return path
