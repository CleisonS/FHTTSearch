from dataclasses import dataclass, field
@dataclass
class ReadinessItem:
    detected: bool=False; backend: str=""; control_type: str=""; class_name: str=""; automation_id: str=""; handle: int=0; rectangle: dict=field(default_factory=dict); confidence_score: int=0; notes: list[str]=field(default_factory=list); capabilities: dict=field(default_factory=dict)
@dataclass
class ReadinessResult:
    search_field: ReadinessItem=field(default_factory=ReadinessItem); onu_table: ReadinessItem=field(default_factory=ReadinessItem); device_tree: ReadinessItem=field(default_factory=ReadinessItem); onu_list_tab: ReadinessItem=field(default_factory=ReadinessItem); columns: dict=field(default_factory=dict); classification: str="UNKNOWN"; recommendation: str="Insufficient information"; confidence_score: int=0; notes: list[str]=field(default_factory=list)
