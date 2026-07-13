from dataclasses import dataclass, field
from app.models.window_info import WindowInfo
from app.models.backend_result import BackendResult
from app.models.control_info import ControlInfo
from app.models.readiness_result import ReadinessResult
@dataclass
class InspectionResult:
    window: WindowInfo|None=None; win32_result: BackendResult|None=None; uia_result: BackendResult|None=None; controls_win32: list[ControlInfo]=field(default_factory=list); controls_uia: list[ControlInfo]=field(default_factory=list); readiness: ReadinessResult|None=None; errors: list[str]=field(default_factory=list); timings: dict=field(default_factory=dict)
