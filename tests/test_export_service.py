import json
from app.models.control_info import ControlInfo
from app.models.inspection_result import InspectionResult
from app.models.readiness_result import ReadinessResult
from app.services.export_service import ExportService

def test_exports(tmp_path):
    c=ControlInfo(index=0,backend='uia',name='Search',control_type='Edit',rectangle={'left':0,'top':0,'right':10,'bottom':10})
    res=InspectionResult(controls_uia=[c], readiness=ReadinessResult())
    ex=ExportService()
    assert ex.export_txt(res,tmp_path/'r.txt').exists()
    assert ex.export_json(res,tmp_path/'r.json').exists()
    assert json.loads((tmp_path/'r.json').read_text(encoding='utf-8'))['controls_uia'][0]['name']=='Search'
    assert ex.export_controls_csv([c],tmp_path/'c.csv').read_text(encoding='utf-8-sig').startswith('index;')
