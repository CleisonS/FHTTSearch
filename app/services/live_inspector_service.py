from __future__ import annotations

import os

from app.models.control_info import ControlInfo
from app.services.process_service import ProcessService
from app.utils.safe_calls import safe_get


class LiveInspectorService:
    def inspect_at_cursor(self, backend: str = "uia") -> ControlInfo:
        if os.name != "nt":
            return ControlInfo(backend=backend, errors=["Live Inspector requer Windows."])
        import win32api
        import win32gui
        from pywinauto import Desktop

        x, y = win32api.GetCursorPos()
        hwnd = int(safe_get(lambda: win32gui.WindowFromPoint((x, y)), 0, "WindowFromPoint") or 0)
        title = safe_get(lambda: win32gui.GetWindowText(hwnd), "", "GetWindowText") or ""
        import win32process
        _, pid = safe_get(lambda: win32process.GetWindowThreadProcessId(hwnd), (0, 0), "GetWindowThreadProcessId")
        process = ProcessService().get_process_data(pid).get("name", "") if pid else ""
        info = ControlInfo(
            backend=backend,
            handle=hwnd,
            process_id=int(pid or 0),
            name=title,
            text=f"X={x}; Y={y}; Processo={process}",
            rectangle={"left": x, "top": y, "right": x, "bottom": y},
        )
        try:
            wrapper = Desktop(backend=backend).from_point(x, y)
            info.name = wrapper.element_info.name or info.name
            info.text = wrapper.window_text() or info.text
            info.control_type = wrapper.element_info.control_type or ""
            info.class_name = wrapper.element_info.class_name or ""
            info.automation_id = getattr(wrapper.element_info, "automation_id", "") or ""
            rect = wrapper.rectangle()
            info.rectangle = {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}
            info.process_id = wrapper.element_info.process_id
            info.enabled = wrapper.is_enabled()
            info.visible = wrapper.is_visible()
            info.children_count = len(wrapper.children())
        except Exception as exc:
            info.errors.append(str(exc))
        return info
