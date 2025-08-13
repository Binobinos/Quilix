import os
import sys

from PyQt6.QtWidgets import (
    QApplication
)

from modern_browser import ModernBrowser

if __name__ == "__main__":
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox'
    app = QApplication(sys.argv)
    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec())
