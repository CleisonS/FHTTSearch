import os

import pytest

from app.services.window_service import WindowService


def test_window_service_non_windows_raises():
    if os.name == "nt":
        pytest.skip("Teste específico para ambiente não Windows")
    with pytest.raises(RuntimeError, match="somente no Windows"):
        WindowService().list_windows()
