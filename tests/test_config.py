import pytest
pytest.importorskip('PySide6')
from app.bootstrap import load_config

def test_corrupt_config_recovers(tmp_path):
    p=tmp_path/'config.json'; p.write_text('{bad',encoding='utf-8')
    cfg=load_config(p)
    assert cfg['inspection_max_depth']==20
    assert p.with_suffix('.corrupted.bak').exists()
