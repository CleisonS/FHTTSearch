from __future__ import annotations

import time
from collections import Counter

from app.models.backend_result import BackendResult
from app.utils.safe_calls import safe_get

MEANINGFUL_TYPES = {"Edit", "Tree", "Table", "DataGrid", "List", "Tab", "Button", "Header", "DataItem"}


class BackendDetector:
    def detect_backend(self, hwnd: int, backend: str) -> BackendResult:
        started = time.time()
        result = BackendResult(backend=backend, handle_valid=bool(hwnd))
        try:
            wrapper = self._connect_window(hwnd, backend)
            result.success = wrapper is not None
            if not wrapper:
                result.error = "Janela não encontrada pelo backend."
                return result
            title = safe_get(lambda: wrapper.window_text(), None, "window_text")
            element = safe_get(lambda: wrapper.element_info, None, "element_info")
            if not title and element is not None:
                title = safe_get(lambda: element.name, "", "element_info.name")
            result.title_accessible = title is not None
            descendants = safe_get(lambda: wrapper.descendants(), [], "descendants") or []
            result.controls_count = len(descendants)
            names = []
            control_types = []
            automation_ids = []
            for child in descendants:
                info = safe_get(lambda child=child: child.element_info, None, "child.element_info")
                name = safe_get(lambda info=info: info.name, "", "child.name") if info is not None else ""
                ctype = safe_get(lambda info=info: info.control_type, "", "child.control_type") if info is not None else ""
                auto_id = safe_get(lambda info=info: info.automation_id, "", "child.automation_id") if info is not None else ""
                if name:
                    names.append(name)
                if ctype:
                    control_types.append(ctype)
                if auto_id:
                    automation_ids.append(auto_id)
            result.named_controls_count = len(names)
            result.meaningful_controls_count = sum(1 for ctype in control_types if ctype in MEANINGFUL_TYPES)
            result.score = self._score(result, control_types, automation_ids)
        except Exception as exc:
            result.error = str(exc)
        finally:
            result.duration_ms = int((time.time() - started) * 1000)
        return result

    def _connect_window(self, hwnd: int, backend: str):
        from pywinauto import Application, Desktop

        app_wrapper = safe_get(lambda: Application(backend=backend).connect(handle=hwnd, timeout=3).window(handle=hwnd), None, "Application.connect")
        if app_wrapper is not None and safe_get(lambda: app_wrapper.exists(timeout=1), True, "app_wrapper.exists"):
            return app_wrapper
        desktop_wrapper = safe_get(lambda: Desktop(backend=backend).window(handle=hwnd), None, "Desktop.window")
        if desktop_wrapper is not None and safe_get(lambda: desktop_wrapper.exists(timeout=1), True, "desktop_wrapper.exists"):
            return desktop_wrapper
        return None

    def _score(self, result: BackendResult, control_types: list[str], automation_ids: list[str]) -> int:
        type_counts = Counter(control_types)
        diversity = len(type_counts)
        custom_penalty = 20 if result.controls_count and type_counts.get("Custom", 0) + type_counts.get("Pane", 0) == result.controls_count else 0
        raw = (
            min(result.controls_count, 200)
            + result.named_controls_count * 2
            + result.meaningful_controls_count * 10
            + len(automation_ids) * 3
            + diversity * 5
            - custom_penalty
        )
        return max(0, min(100, raw))

    def detect(self, hwnd: int) -> tuple[BackendResult, BackendResult, str]:
        win32 = self.detect_backend(hwnd, "win32")
        uia = self.detect_backend(hwnd, "uia")
        if not win32.success and not uia.success:
            classification = "NO_ACCESS"
        elif win32.success and uia.success and abs(win32.score - uia.score) <= 20:
            classification = "HYBRID_RECOMMENDED"
        elif win32.score > uia.score:
            classification = "WIN32_RECOMMENDED"
        elif uia.score > win32.score:
            classification = "UIA_RECOMMENDED"
        else:
            classification = "LIMITED_ACCESS"
        win32.classification = uia.classification = classification
        return win32, uia, classification
