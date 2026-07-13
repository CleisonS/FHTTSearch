from app.models.control_info import ControlInfo
from app.utils.serialization import to_plain
from app.utils.file_utils import sanitize_filename

def test_dataclass_serialization_and_sanitize():
    c=ControlInfo(index=1,name='Search',rectangle={'left':1,'top':2,'right':11,'bottom':22})
    d=to_plain(c)
    assert d['name']=='Search'
    assert sanitize_filename('FH_FB-DC - NE Manager: 172.16.8.70').endswith('172.16.8.70')
