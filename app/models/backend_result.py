from dataclasses import dataclass, field


@dataclass
class BackendResult:
    backend: str
    success: bool = False
    handle_valid: bool = False
    title_accessible: bool = False
    controls_count: int = 0
    named_controls_count: int = 0
    meaningful_controls_count: int = 0
    duration_ms: int = 0
    error: str = ""
    score: int = 0
    classification: str = "UNKNOWN"
    has_edit: bool = False
    has_tree: bool = False
    has_table: bool = False
    has_list: bool = False
    has_tab: bool = False
    has_button: bool = False
    has_datagrid: bool = False
    has_custom: bool = False
    control_type_counts: dict[str, int] = field(default_factory=dict)
