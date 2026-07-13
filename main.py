from app.bootstrap import create_app
from app.ui.main_window import MainWindow

def main() -> int:
    app, config = create_app()
    win = MainWindow(config)
    win.show()
    return app.exec()
if __name__ == '__main__':
    raise SystemExit(main())
