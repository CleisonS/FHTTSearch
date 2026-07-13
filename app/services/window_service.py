from __future__ import annotations

import logging
import os
from collections.abc import Iterable

from app.constants import DEFAULT_UNM_FILTERS
from app.models.window_info import WindowInfo
from app.services.process_service import ProcessService
from app.utils.safe_calls import safe_get

LOG = logging.getLogger(__name__)

NE_MANAGER_MARKERS = ("ne manager", "fh_", "fh-")


def _rect_dict(rect) -> dict:
    if not rect:
        return {"left": 0, "top": 0, "right": 0, "bottom": 0}
    if isinstance(rect, tuple):
        return {"left": rect[0], "top": rect[1], "right": rect[2], "bottom": rect[3]}
    return {
        "left": int(getattr(rect, "left", 0) or 0),
        "top": int(getattr(rect, "top", 0) or 0),
        "right": int(getattr(rect, "right", 0) or 0),
        "bottom": int(getattr(rect, "bottom", 0) or 0),
    }


def is_unm_candidate(w: WindowInfo) -> bool:
    hay = f"{w.title} {w.process_name} {w.class_name} {w.executable_path}".lower()
    return any(marker.lower() in hay for marker in DEFAULT_UNM_FILTERS) or any(marker in hay for marker in NE_MANAGER_MARKERS)


def matches_window_filter(w: WindowInfo, text: str = "", only_unm: bool = False, only_visible: bool = False) -> bool:
    hay = f"{w.title} {w.process_name} {w.class_name} {w.executable_path}".lower()
    if only_visible and not w.visible:
        return False
    if only_unm and not is_unm_candidate(w):
        return False
    return not text or text.lower() in hay


class WindowService:
    """Lista janelas por Win32 e complementa títulos/handles com UIA.

    Algumas janelas Java/Swing/SWT do UNM2000/NE Manager podem aparecer com título
    vazio no Win32 ou como owned/tool windows. Por isso a listagem combina
    EnumWindows, Desktop(backend="uia").windows() e uma varredura limitada de
    filhos candidatos, deduplicando por handle.
    """

    def __init__(self) -> None:
        self.process_service = ProcessService()

    def list_windows(self) -> list[WindowInfo]:
        if os.name != "nt":
            return []
        windows: dict[int, WindowInfo] = {}
        self._merge(windows, self._list_win32_top_level())
        self._merge(windows, self._list_uia_top_level())
        self._merge(windows, self._list_candidate_child_windows(windows.values()))
        return sorted(windows.values(), key=lambda w: (not is_unm_candidate(w), not w.visible, w.title.lower(), w.handle))

    def _merge(self, target: dict[int, WindowInfo], found: Iterable[WindowInfo]) -> None:
        for item in found:
            if not item.handle:
                continue
            current = target.get(item.handle)
            if current is None:
                target[item.handle] = item
                continue
            current.title = current.title or item.title
            current.class_name = current.class_name or item.class_name
            current.process_name = current.process_name or item.process_name
            current.executable_path = current.executable_path or item.executable_path
            current.rectangle = current.rectangle or item.rectangle
            current.visible = current.visible or item.visible
            current.minimized = current.minimized or item.minimized
            current.maximized = current.maximized or item.maximized
            current.uia_available = current.uia_available or item.uia_available
            current.win32_available = current.win32_available or item.win32_available
            if item.source not in current.source.split("+"):
                current.source = f"{current.source}+{item.source}"

    def _base_from_hwnd(self, hwnd: int, source: str, parent_handle: int = 0, is_top_level: bool = True) -> WindowInfo:
        import win32gui
        import win32process

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        pdata = self.process_service.get_process_data(pid)
        rect = safe_get(lambda: win32gui.GetWindowRect(hwnd), (0, 0, 0, 0), "GetWindowRect")
        return WindowInfo(
            title=safe_get(lambda: win32gui.GetWindowText(hwnd), "", "GetWindowText") or "",
            handle=int(hwnd),
            pid=int(pid or 0),
            process_name=pdata.get("name", ""),
            executable_path=pdata.get("exe", ""),
            class_name=safe_get(lambda: win32gui.GetClassName(hwnd), "", "GetClassName") or "",
            rectangle=_rect_dict(rect),
            visible=bool(safe_get(lambda: win32gui.IsWindowVisible(hwnd), False, "IsWindowVisible")),
            minimized=bool(safe_get(lambda: win32gui.IsIconic(hwnd), False, "IsIconic")),
            maximized=bool(safe_get(lambda: win32gui.IsZoomed(hwnd), False, "IsZoomed")),
            win32_available=True,
            source=source,
            parent_handle=parent_handle,
            owner_handle=int(safe_get(lambda: win32gui.GetWindow(hwnd, 4), 0, "GetWindowOwner") or 0),
            is_top_level=is_top_level,
        )

    def _list_win32_top_level(self) -> list[WindowInfo]:
        import win32gui

        out: list[WindowInfo] = []

        def callback(hwnd, _):
            try:
                out.append(self._base_from_hwnd(hwnd, "win32"))
            except Exception as exc:  # pragma: no cover - depends on live Windows handles
                LOG.debug("Falha ao coletar HWND %s por Win32: %s", hwnd, exc)
            return True

        win32gui.EnumWindows(callback, None)
        return out

    def _list_uia_top_level(self) -> list[WindowInfo]:
        try:
            from pywinauto import Desktop
        except Exception as exc:  # pragma: no cover - dependency optional outside Windows
            LOG.debug("UIA indisponível para listagem de janelas: %s", exc)
            return []

        out: list[WindowInfo] = []
        for wrapper in safe_get(lambda: Desktop(backend="uia").windows(), [], "Desktop.uia.windows") or []:
            hwnd = int(safe_get(lambda: wrapper.handle, 0, "uia.handle") or 0)
            if not hwnd:
                continue
            item = safe_get(lambda: self._base_from_hwnd(hwnd, "uia"), None, "base_from_uia_hwnd")
            if item is None:
                continue
            item.title = safe_get(lambda: wrapper.window_text(), item.title, "uia.window_text") or item.title
            info = safe_get(lambda: wrapper.element_info, None, "uia.element_info")
            if info is not None:
                item.title = safe_get(lambda: info.name, item.title, "uia.name") or item.title
                item.class_name = safe_get(lambda: info.class_name, item.class_name, "uia.class_name") or item.class_name
                item.pid = int(safe_get(lambda: info.process_id, item.pid, "uia.process_id") or item.pid)
            item.uia_available = True
            out.append(item)
        return out

    def _list_candidate_child_windows(self, top_windows: Iterable[WindowInfo]) -> list[WindowInfo]:
        """Inclui filhos/owned windows candidatos a NE Manager quando o top-level não tem título útil."""
        import win32gui

        pids = {w.pid for w in top_windows if is_unm_candidate(w) or self._looks_like_java_or_unm_process(w)}
        if not pids:
            return []
        out: list[WindowInfo] = []

        def collect_child(parent: WindowInfo) -> None:
            def callback(hwnd, _):
                item = safe_get(lambda: self._base_from_hwnd(hwnd, "win32-child", parent.handle, False), None, "child_window")
                if item and item.pid in pids and (item.title or is_unm_candidate(item)):
                    out.append(item)
                return True
            win32gui.EnumChildWindows(parent.handle, callback, None)

        for top in top_windows:
            if top.pid in pids:
                collect_child(top)
        return out

    def _looks_like_java_or_unm_process(self, w: WindowInfo) -> bool:
        hay = f"{w.process_name} {w.executable_path}".lower()
        return any(name in hay for name in ("java", "javaw", "unm", "fiber", "fh"))
