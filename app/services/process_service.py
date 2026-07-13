from __future__ import annotations
try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None
class ProcessService:
    def get_process_data(self, pid: int) -> dict:
        if psutil is None:
            return {"name": "", "exe": "", "error": "psutil indisponível"}
        try:
            p = psutil.Process(pid)
            return {"name": p.name(), "exe": p.exe(), "username": p.username(), "status": p.status()}
        except Exception as exc:
            return {"name": "", "exe": "", "error": str(exc)}
