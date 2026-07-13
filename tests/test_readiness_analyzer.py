from app.models.control_info import ControlInfo
from app.services.readiness_analyzer import ReadinessAnalyzer

def test_readiness_detects_unm_elements():
    controls=[
        ControlInfo(index=0,backend='uia',name='Search',control_type='Edit',keyboard_focusable=True),
        ControlInfo(index=1,backend='uia',name='ONU List',control_type='Table'),
        ControlInfo(index=2,backend='uia',name='Device Tree',control_type='Tree'),
        ControlInfo(index=3,backend='uia',name='ONU Status',control_type='Header'),
        ControlInfo(index=4,backend='uia',name='Device Name',control_type='Header'),
        ControlInfo(index=5,backend='uia',name='Physical Address',control_type='Header'),
    ]
    r=ReadinessAnalyzer().analyze(controls)
    assert r.search_field.detected
    assert r.onu_table.detected
    assert r.device_tree.detected
    assert {'ONU Status','Device Name','Physical Address'} <= set(r.columns)
    assert r.classification in {'GOOD','EXCELLENT'}
