import os
from typing import Any

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QGuiApplication, QIcon
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMenu, QMessageBox
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
        self.webview.page().setInspectedPage(self.webview.page())
        """DevTools"""
        self.webview.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        self.webview.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.webview.setUrl(QUrl(url))
        self.layout.addWidget(self.webview)
        self.layout.addWidget(self.note_area)
        self.setLayout(self.layout)
        self.tab_id = tab_id or os.urandom(8).hex()
        self.parent = parent
        self._dev_window = None
        self._dev_view = None

    def page_context_menu(self, pos):
        """Custom page context menu"""
        try:
            menu = QMenu(self)

            back_action = QAction(QIcon.fromTheme("go-previous"), "Back", self)
            back_action.triggered.connect(self.webview.back)
            back_action.setEnabled(self.webview.history().canGoBack())

            forward_action = QAction(QIcon.fromTheme("go-next"), "Forward", self)
            forward_action.triggered.connect(self.webview.forward)
            forward_action.setEnabled(self.webview.history().canGoForward())

            reload_action = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
            reload_action.triggered.connect(self.webview.reload)

            copy_url_action = QAction(QIcon.fromTheme("edit-copy"), "Copy URL", self)
            copy_url_action.triggered.connect(self.copy_current_url)

            paste_url_action = QAction(QIcon.fromTheme("edit-paste"), "Paste URL", self)
            paste_url_action.triggered.connect(self.paste_url)  # Обновлено

            open_new_tab_action = QAction(QIcon.fromTheme("tab-new"), "Open in New Tab", self)
            open_new_tab_action.triggered.connect(self.open_in_new_tab)

            inspect_action = QAction(QIcon.fromTheme("applications-development"), "Inspect", self)
            inspect_action.triggered.connect(self.inspect_page)

            menu.addAction(back_action)
            menu.addAction(forward_action)
            menu.addAction(reload_action)
            menu.addSeparator()
            menu.addAction(copy_url_action)
            menu.addAction(paste_url_action)
            menu.addAction(open_new_tab_action)
            menu.addSeparator()
            menu.addAction(inspect_action)

            menu.exec(self.webview.mapToGlobal(pos))

        except Exception as e:
            print(f"Error in context menu: {e}")
            import traceback
            traceback.print_exc()

    def inspect_page(self):
        """Opens the developer tools while keeping a link to the window"""
        try:
            if hasattr(self, '_dev_window') and self._dev_window:
                self._dev_window.show()
                self._dev_window.raise_()
                return

            from PyQt6.QtWidgets import QMainWindow
            self._dev_window = QMainWindow()
            self._dev_window.setWindowTitle(f"Developer Tools - {self.webview.title()}")
            self._dev_window.resize(1024, 768)

            self._dev_view = QWebEngineView(self._dev_window)
            self._dev_window.setCentralWidget(self._dev_view)

            self.webview.page().setDevToolsPage(self._dev_view.page())

            self._dev_window.destroyed.connect(self._on_devtools_close)

            self._dev_window.show()

        except Exception as e:
            print(f"Error opening dev tools: {e}")
            QMessageBox.warning(
                self,
                "Inspect Error",
                "Failed to open developer tools.\n"
                f"Error: {str(e)}"
            )

    def _on_devtools_close(self):
        """Clearing links when closing the developer window"""
        self._dev_window = None
        self._dev_view = None

    def copy_current_url(self):
        url = self.webview.url().toString()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(url)

    def paste_url(self):
        """Pastes the URL from the clipboard into the address bar or the current page"""
        clipboard = QGuiApplication.clipboard()
        url = clipboard.text().strip()

        if url:
            self.webview.page().runJavaScript(f"""
                const activeElement = document.activeElement;
                if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {{
                    const start = activeElement.selectionStart;
                    const end = activeElement.selectionEnd;
                    activeElement.value = activeElement.value.substring(0, start) + `{url}` + activeElement.value.substring(end);
                    activeElement.selectionStart = activeElement.selectionEnd = start + {len(url)};
                }} else {{
                    if ({QUrl(url).isValid()} && (`{url}`.startsWith('http://') || `{url}`.startsWith('https://'))) {{
                        window.location = `{url}`;
                    }}
                }}
            """)

    def open_in_new_tab(self):
        url = self.webview.url().toString()
        self.parent.add_tab(url)

