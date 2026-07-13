from __future__ import annotations
import zipfile
from pathlib import Path
from app.services.export_service import ExportService
from app.services.screenshot_service import ScreenshotService
from app.utils.file_utils import ensure_dir, timestamp, copy_if_exists
from app.utils.win_utils import environment_summary
class ReportService:
    def create_full_report(self, inspection, windows, base: Path = Path('output/reports')):
        folder = ensure_dir(base / f"{timestamp()}_UNM_Inspection"); ex = ExportService()
        ex.export_txt(inspection, folder / 'report.txt'); ex.export_json({'environment': environment_summary(), 'inspection': inspection}, folder / 'report.json')
        ex.export_windows_csv(windows, folder / 'windows.csv'); ex.export_controls_csv(inspection.controls_win32, folder / 'controls_win32.csv'); ex.export_controls_csv(inspection.controls_uia, folder / 'controls_uia.csv')
        if inspection.readiness: ex.export_readiness_csv(inspection.readiness, folder / 'readiness.csv')
        (folder / 'environment.txt').write_text('\n'.join(f'{k}: {v}' for k, v in environment_summary().items()), encoding='utf-8')
        copy_if_exists(Path('logs/unm_inspector.log'), folder / 'application.log')
        try:
            ss = ScreenshotService(folder); ss.capture_desktop()
            if inspection.window: ss.capture_window(inspection.window)
        except Exception as exc:
            (folder / 'screenshot_error.txt').write_text(str(exc), encoding='utf-8')
        zip_path = folder.with_suffix('.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in folder.rglob('*'): z.write(p, p.relative_to(folder.parent))
        return folder, zip_path
