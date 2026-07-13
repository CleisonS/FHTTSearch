from app.models.window_info import WindowInfo
from app.services.window_service import matches_window_filter

def test_window_filters():
    w=WindowInfo(title='FH_FB-DC - NE Manager - 172.16.8.70',process_name='unm.exe',visible=True)
    assert matches_window_filter(w,only_unm=True)
    assert matches_window_filter(w,'manager')
    assert not matches_window_filter(WindowInfo(title='Calc',visible=False),only_visible=True)
