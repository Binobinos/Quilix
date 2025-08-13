import os
from typing import Any

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from config.config import (
    HOME_URL
)


class BrowserTab(QWidget):
    def __init__(
            self,
            url: str = HOME_URL,
            tab_id: Any = None) \
            -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.webview = QWebEngineView()
        self.note_area = QTextEdit()
        self.note_area.setPlaceholderText("Tab notes (exclusive feature)")
        self.note_area.setMaximumHeight(80)
        self.note_area.setVisible(False)

        # Enable modern web features
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        self.webview.setUrl(QUrl(url))
        self.layout.addWidget(self.webview)
        self.layout.addWidget(self.note_area)
        self.setLayout(self.layout)
        self.tab_id = tab_id or os.urandom(8).hex()
