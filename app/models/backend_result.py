from dataclasses import dataclass
@dataclass
class BackendResult:
    backend:str; success:bool=False; handle_valid:bool=False; title_accessible:bool=False; controls_count:int=0; named_controls_count:int=0; meaningful_controls_count:int=0; duration_ms:int=0; error:str=""; score:int=0; classification:str="UNKNOWN"
