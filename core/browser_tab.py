import os
from typing import Any

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QGuiApplication
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
            parent: "ModernBrowser",
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
        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.webview.customContextMenuRequested.connect(self.page_context_menu)
        self.webview.setUrl(QUrl(url))
        self.layout.addWidget(self.webview)
        self.layout.addWidget(self.note_area)
        self.setLayout(self.layout)
        self.tab_id = tab_id or os.urandom(8).hex()
        self.parent = parent

    def page_context_menu(self, pos):
        """Контекстное меню при клике правой кнопкой на странице."""
        menu = self.webview.createStandardContextMenu()

        copy_url_action = QAction("Copy URL", self)
        copy_url_action.triggered.connect(self.copy_current_url)

        open_new_tab_action = QAction("Open in New Tab", self)
        open_new_tab_action.triggered.connect(self.open_in_new_tab)

        menu.addSeparator()
        menu.addAction(copy_url_action)
        menu.addAction(open_new_tab_action)

        menu.exec(self.webview.mapToGlobal(pos))

    def copy_current_url(self):
        url = self.webview.url().toString()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(url)

    def open_in_new_tab(self):
        url = self.webview.url().toString()
        self.parent.add_tab(url)

