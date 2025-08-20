"""
Browser tab implementation for ModernBrowser.

This module provides the BrowserTab class which represents a single browser tab
with web browsing capabilities, developer tools integration, and note-taking features.
"""

import os
from typing import Any

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QGuiApplication, QIcon, QShortcut
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QMenu,
    QMessageBox,
    QMainWindow,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from config.config import PAGE_URL


class BrowserTab(QWidget):
    """A single browser tab with web view, developer tools, and note-taking functionality.

    Attributes:
        webview (QWebEngineView): The main web view component for browsing.
        note_area (QTextEdit): Text area for tab-specific notes.
        tab_id (str): Unique identifier for the tab.
        parent (ModernBrowser): Reference to the parent browser window.
        _dev_window (QMainWindow): Developer tools window.
        _dev_view (QWebEngineView): Web view for developer tools.
    """

    def __init__(
        self, parent: "ModernBrowser", url: str = PAGE_URL, tab_id: Any = None
    ) -> None:
        """
        Initialize a new browser tab.

        Args:
            parent: Reference to the parent ModernBrowser instance.
            url: Initial URL to load (defaults to HOME_URL).
            tab_id: Optional unique identifier for the tab (generated if None).

        The tab includes:
        - A fully-featured web view with modern web capabilities enabled
        - A collapsible note-taking area
        - Context menu with browsing actions
        - Integrated developer tools
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.webview = QWebEngineView()
        self.note_area = QTextEdit()
        self.note_area.setPlaceholderText("Tab notes (exclusive feature)")
        self.note_area.setMaximumHeight(80)
        self.note_area.setVisible(False)

        # Configure web engine settings
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True
        )
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
        )

        self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.webview.customContextMenuRequested.connect(self.page_context_menu)
        self.webview.page().setInspectedPage(self.webview.page())
        # Enable DevTools support
        self.webview.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        self.webview.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

        if url == PAGE_URL:
            self.webview.setUrl(QUrl.fromLocalFile(os.path.abspath(PAGE_URL)))
        else:
            self.webview.setUrl(QUrl(url))
        self.layout.addWidget(self.webview)
        self.layout.addWidget(self.note_area)
        self.setLayout(self.layout)
        self.tab_id = tab_id or os.urandom(8).hex()
        self.parent = parent
        self._dev_window = None
        self._dev_view = None

    def page_context_menu(self, pos):
        """
        Display a custom context menu for the web page.

        Args:
            pos: The position where the context menu was requested.

        The context menu includes:
        - Navigation actions (back, forward, reload)
        - URL actions (copy, paste)
        - Tab management (open in new tab)
        - Developer tools access
        """
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

            copy_text_action = QAction(QIcon.fromTheme("edit-copy"), "Copy Text", self)
            copy_text_action.triggered.connect(self.copy_text)

            paste_text_action = QAction(
                QIcon.fromTheme("edit-paste"), "Paste Text", self
            )
            paste_text_action.triggered.connect(self.paste_text)

            cut_text_action = QAction(QIcon.fromTheme("edit-cut"), "Cut Text", self)
            cut_text_action.triggered.connect(self.cut_text)

            copy_url_action = QAction(QIcon.fromTheme("edit-copy"), "Copy URL", self)
            copy_url_action.triggered.connect(self.copy_current_url)

            paste_url_action = QAction(QIcon.fromTheme("edit-paste"), "Paste URL", self)
            paste_url_action.triggered.connect(self.paste_url)

            open_new_tab_action = QAction(
                QIcon.fromTheme("tab-new"), "Open in New Tab", self
            )
            open_new_tab_action.triggered.connect(self.open_in_new_tab)

            inspect_action = QAction(
                QIcon.fromTheme("applications-development"), "Inspect", self
            )
            inspect_action.triggered.connect(self.inspect_page)

            menu.addAction(back_action)
            menu.addAction(forward_action)
            menu.addAction(reload_action)
            menu.addSeparator()
            menu.addAction(copy_text_action)
            menu.addAction(cut_text_action)
            menu.addAction(paste_text_action)
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

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        QShortcut("Ctrl+C", self.webview, self.copy_text)
        QShortcut("Ctrl+V", self.webview, self.paste_text)
        QShortcut("Ctrl+X", self.webview, self.cut_text)

    def copy_text(self):
        """Copy selected text to clipboard."""
        self.webview.page().triggerAction(QWebEnginePage.WebAction.Copy)

    def paste_text(self):
        """Paste text from clipboard into focused input field."""
        self.webview.page().triggerAction(QWebEnginePage.WebAction.Paste)

    def cut_text(self):
        """Cut selected text to clipboard."""
        self.webview.page().triggerAction(QWebEnginePage.WebAction.Cut)

    def inspect_page(self):
        """
        Open developer tools in a separate window.

        Creates a new QMainWindow containing a web view connected to the
        current page's developer tools. If developer tools are already open,
        brings the existing window to focus.
        """
        try:
            if hasattr(self, "_dev_window") and self._dev_window:
                self._dev_window.show()
                self._dev_window.raise_()
                return

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
                f"Failed to open developer tools.\nError: {str(e)}",
            )

    def _on_devtools_close(self):
        """Clean up references when developer tools window is closed."""
        self._dev_window = None
        self._dev_view = None

    def copy_current_url(self):
        """Copy the current page URL to clipboard."""
        url = self.webview.url().toString()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(url)

    def paste_url(self):
        """Pastes URL from clipboard into current page.

        Attempts to intelligently paste the URL either into a focused input field
        or navigate to it directly if it's a valid URL.
        """
        clipboard = QGuiApplication.clipboard()
        if url := clipboard.text().strip():
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
        """Open the current page URL in a new tab."""
        url = self.webview.url().toString()
        self.parent.add_tab(url)
