import os
import sys

from PyQt6.QtWidgets import (
    QApplication
)

from modern_browser import ModernBrowser

if __name__ == "__main__":
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = (
        '--no-sandbox '
        '--remote-allow-origins=* '
        '--enable-devtools-experiments'
    )
    app = QApplication(sys.argv)
    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec())
