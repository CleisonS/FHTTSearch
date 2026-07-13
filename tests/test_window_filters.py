from app.models.window_info import WindowInfo
from app.services.window_service import is_unm_candidate, matches_window_filter


def test_window_filters_match_ne_manager():
    w = WindowInfo(title="FH_FB-DC - NE Manager - 172.16.8.70", process_name="javaw.exe", visible=True)
    assert is_unm_candidate(w)
    assert matches_window_filter(w, only_unm=True)
    assert matches_window_filter(w, "manager")


def test_window_filters_match_olt_without_ne_manager_text():
    w = WindowInfo(title="FH_DV-DC", process_name="javaw.exe", class_name="SunAwtFrame", visible=True)
    assert is_unm_candidate(w)
    assert matches_window_filter(w, only_unm=True)


def test_window_filters_visible_flag():
    assert not matches_window_filter(WindowInfo(title="Calc", visible=False), only_visible=True)
