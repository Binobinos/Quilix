import os
import sys

from PyQt6.QtWidgets import (
    QApplication
)

from modern_browser import ModernBrowser

if __name__ == "__main__":
    os.environ["QT_STYLE_OVERRIDE"] = ""
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = (
        '--no-sandbox '
        '--remote-allow-origins=* '
        '--enable-devtools-experiments'
    )
    app = QApplication(sys.argv)
    browser = ModernBrowser(app)
    browser.show()
    sys.exit(app.exec())
