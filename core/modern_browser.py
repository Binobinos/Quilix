"""
ModernBrowser - A feature-rich Qt-based web browser implementation.

This module provides the main browser window class with tabbed browsing,
session management, note-taking, and productivity features.
"""

import os
from typing import Any

from PyQt6.QtCore import QPoint, Qt, QTimer, QUrl, QSize, QSettings
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTabWidget,
    QToolBar,
    QWidget,
    QApplication,
    QTabBar,
)

from browser_tab import BrowserTab
from config.config import (
    HISTORY_FILE,
    PAGE_URL,
    ICON_DIR,
    DARK_STYLE,
    LIGHT_STYLE,
    __version__,
)
from core.config.config import HOME_URL
from core.model.setting_model import ItemHistory
from util import save_json, create_dir, load_css


class ModernBrowser(QMainWindow):
    """
    Main browser window implementing tabbed browsing and productivity features.

    Attributes:
        parent_app (QApplication): Reference to the main application instance
        session (list): List of saved session tabs
        history (list): Browsing history records
        notes (dict): Tab-specific notes
        pomodoro_timer (QTimer): Timer for pomodoro functionality
        pomodoro_state (str): Current pomodoro state
        pomodoro_time (int): Remaining pomodoro time in seconds
        tabs (QTabWidget): Tab management widget
        navbar (QToolBar): Navigation toolbar
        is_fullscreen (bool): Fullscreen state flag
    """

    def __init__(self, app: QApplication) -> None:
        """
        Initialize the browser window with default state and UI.

        Args:
            app: The main QApplication instance

        Initializes:
        - Browser state (session, bookmarks, history, settings, notes)
        - UI components (tabs, toolbar, address bar)
        - Productivity features (pomodoro timer)
        - Default styling and initial tab
        """
        super().__init__()
        self.parent_app = app
        self.setWindowTitle(__version__)

        self.settings = QSettings("Quilix", "Quilix")
        size = self.settings.value("window/size", QSize(1400, 900))
        position = self.settings.value("window/position", QPoint(0, 0))
        self.resize(size)
        self.move(position)

        self.dark_mode = self.settings.value("appearance/dark_mode", False, type=bool)
        self.home_url = self.settings.value("navigation/home_url", HOME_URL)
        self.session = self.settings.value("session/last_session", [])
        self.session_index = self.settings.value(
            "session/last_session_index", 0, type=int
        )
        self.history = self.settings.value("history/items", [])
        self.notes = self.settings.value("notes/all", {})

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.web_view.page().profile().downloadRequested.connect(self.handle_download)
        self.pomodoro_timer = QTimer(self)
        self.pomodoro_state = self.settings.value("pomodoro/state", "idle")
        self.pomodoro_time = self.settings.value("pomodoro/time", 0)

        # --- UI Initialization ---
        self._init_tab_widget()
        self._init_navigation_bar()
        self.is_fullscreen = self.settings.value("window/fullscreen", True)
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.apply_dark_mode(not self.settings.value("mode/dark", type=bool))
        self.add_plus_tab()
        self.restore_session()
        self.pomodoro_timer.timeout.connect(self.pomodoro_tick)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        self.settings.setValue("appearance/dark_mode", self.dark_mode)
        self.settings.setValue("navigation/home_url", self.home_url)
        self.settings.setValue("session/last_session_index", self.session_index)
        self.settings.setValue("history/items", self.history)
        self.settings.setValue("notes/all", self.notes)
        self.settings.setValue("window/fullscreen", self.isFullScreen())
        self.save_session()
        event.accept()

    def _init_tab_widget(self) -> None:
        """Initialize the tab widget with configuration and signals."""
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabBarClicked.connect(self.on_tab_clicked)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_navbar)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self.tab_context_menu)
        self.setCentralWidget(self.tabs)

    def on_tab_clicked(self, index):
        """Обработчик клика по вкладке"""
        if index == self.tabs.count() - 1:
            self.add_tab(self.home_url)

    def _init_navigation_bar(self) -> None:
        """Initialize the navigation toolbar with buttons and actions."""
        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        # Navigation buttons
        self._add_nav_button("arrow_left_dark.png", "←", self.go_back)
        self._add_nav_button("arrow_right_dark.png", "→", self.go_forward)
        self._add_nav_button("refresh_dark.png", "↺", self.reload_page)
        self._add_nav_button("home_dark.png", "🏠", self.go_home)
        self._add_nav_button("fullscreen_dark.png", "⛶", self.toggle_fullscreen)
        self.navbar.addSeparator()

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText(
            "Smart Search: url, bookmarks, actions (note, timer, mute, screenshot...)"
        )
        self.address_bar.returnPressed.connect(self.smart_search)
        self.navbar.addWidget(self.address_bar)

        # Tab and session management
        self.create_path = lambda path: create_dir(ICON_DIR, path)
        # Feature buttons
        self._add_action_button("clock_dark.png", "Pomodoro", self.toggle_pomodoro)
        self._add_action_button("show_notes.png", "Show Notes", self.show_notes)
        self._add_action_button("camera.png", "Screenshot", self.screenshot)
        self._add_action_button("light_mode.png", "Change Theme", self.change_theme)

    def _add_nav_button(self, icon_name: str, text: str, callback) -> None:
        """
        Help to add navigation button to toolbar.

        Args:
            icon_name: Theme icon name
            text: Button text
            callback: Function to connect
        """
        btn = QAction(QIcon(icon_name), text, self)
        btn.triggered.connect(callback)
        self.navbar.addAction(btn)

    def _add_action_button(self, icon_name: str, text: str, callback) -> None:
        """
        Help to add action button to toolbar.

        Args:
            icon_name: Theme icon name
            text: Button text
            callback: Function to connect
        """
        action = QAction(QIcon(icon_name), text, self)
        action.triggered.connect(callback)
        self.navbar.addAction(action)

    def add_plus_tab(self):
        """Добавляет специальную вкладку с плюсиком"""
        self.tabs.addTab(QWidget(), "+")
        self.tabs.tabBar().setTabButton(
            self.tabs.count() - 1, QTabBar.ButtonPosition.RightSide, None
        )

    def add_tab(self, url: str | None = None) -> None:
        """
        Add a new browser tab.

        Args:
            url: URL to load in new tab (defaults to home page)

        Creates a new BrowserTab instance and:
        - Sets up URL change signals
        - Configures title/icon updates
        - Connects note saving
        - Restores any existing notes for the tab
        """
        url = url or self.home_url
        if self.tabs.count() > 0 and self.tabs.tabText(self.tabs.count() - 1) == "+":
            self.tabs.removeTab(self.tabs.count() - 1)
        tab = BrowserTab(self, url=url)
        idx = self.tabs.addTab(tab, "")
        tab.webview.urlChanged.connect(
            lambda qurl, t=tab: self.update_address_bar(qurl, t)
        )
        tab.webview.titleChanged.connect(
            lambda title, i=idx: self.update_tab_title(title, i)
        )
        tab.webview.iconChanged.connect(lambda icon, i=idx: self.set_tab_icon(i, icon))
        tab.webview.urlChanged.connect(lambda qurl, t=tab: self.save_history(qurl, t))
        tab.note_area.textChanged.connect(lambda t=tab: self.save_note(t))
        if tab.tab_id in self.notes:
            tab.note_area.setText(self.notes[tab.tab_id])
        self.tabs.setCurrentIndex(idx)
        self.add_plus_tab()

    def close_tab(self, idx: int) -> None:
        """
        Close the tab at specified index.

        Args:
            idx: Index of tab to close

        Ensures at least one tab remains open by creating
        a new tab if closing the last one.
        """
        if idx != self.tabs.count() - 1:  # Не закрываем плюсик
            self.tabs.removeTab(idx)
            self.tabs.removeTab(self.tabs.count() - 1)
            self.add_plus_tab()
        if self.tabs.count() <= 1:
            self.add_tab()

    def update_navbar(self) -> None:
        """
        Update the navigation bar to reflect the current tab's URL.

        Retrieves the URL from the currently active tab and displays it
        in the address bar. If no tab is active, does nothing.
        """
        if current_tab := self.get_current_tab():
            self.address_bar.setText(current_tab.webview.url().toString())

    def get_current_tab(self) -> BrowserTab | None:
        """
        Retrieve the currently active browser tab.

        Returns:
            The active BrowserTab instance if available, None otherwise.
        """
        return tab if isinstance(tab := self.tabs.currentWidget(), BrowserTab) else None

    def go_back(self) -> None:
        """
        Navigate the current tab back in browsing history.

        If no tab is active or no history exists, does nothing.
        """
        if tab := self.get_current_tab():
            tab.webview.back()

    def go_forward(self) -> None:
        """
        Navigate the current tab forward in browsing history.

        If no tab is active or no forward history exists, does nothing.
        """
        if tab := self.get_current_tab():
            tab.webview.forward()

    def reload_page(self) -> None:
        """
        Reload the current tab's webpage.

        If no tab is active, does nothing.
        """
        if tab := self.get_current_tab():
            tab.webview.reload()

    def go_home(self) -> None:
        """
        Navigate the current tab to the configured home page.

        Uses the URL from settings (defaulting to HOME_URL if not configured).
        If no tab is active, does nothing.
        """
        if tab := self.get_current_tab():
            tab.webview.setUrl(QUrl.fromLocalFile(os.path.abspath(PAGE_URL)))

    def smart_search(self) -> None:
        """
        Process address bar input with intelligent behavior.

        Handles several input types:
        - Special commands (note, mute, screenshot, timer)
        - Bookmark matches (title or URL contains input text)
        - History matches (title or URL contains input text)
        - Direct URLs (with or without http(s):// prefix)
        - Search queries (fallback to Google search)

        The matching is case-insensitive.
        """
        text = self.address_bar.text().strip().lower()
        actions = {
            "note": self.show_notes,
            "mute": self.toggle_mute,
            "screenshot": self.screenshot,
        }
        if not text:
            return

        if func := actions.get(text):
            func()
            return

        if text.startswith("timer"):
            self.toggle_pomodoro()
            return

        for item in reversed(self.history):
            url = item["url"]

            if text.lower() in item["title"].lower() or text.lower() in url.lower():
                self.add_tab(url)
                return

        if "." in text or text.startswith("http"):
            url = text if text.startswith("http") else "https://" + text
            self.add_tab(url)
            return

        self.add_tab("https://www.google.com/search?q=" + text)

    def save_session(self) -> None:
        """
        Save the current browsing session to disk.

        Stores all open tabs' URLs in JSON format. Shows success message
        or silently fails on error (prints exception to console).
        """
        try:
            tab: BrowserTab
            sessions: list[ItemHistory] = [
                {"title": tab.webview.title(), "url": tab.webview.url().toString()}
                for i in range(self.tabs.count())
                if isinstance((tab := self.tabs.widget(i)), BrowserTab)
            ]
            self.settings.setValue("session/last_session", sessions)
            self.settings.setValue(
                "session/last_session_index", self.tabs.currentIndex()
            )
        except Exception as e:
            print(e)

    def restore_session(self) -> None:
        """
        Restore a previously saved browsing session.

        Clears current tabs and recreates them from the saved session file.
        Uses default empty list if no session exists.
        """
        self.tabs.clear()
        if self.session:
            for tab in self.session:
                print(tab)
                self.add_tab(tab["url"])
            self.tabs.setCurrentIndex(self.session_index)
            return
        self.add_tab()

    def save_note(self, tab: BrowserTab) -> None:
        """
        Persist notes for a browser tab.

        Args:
            tab: The BrowserTab instance whose notes should be saved

        Saves notes in JSON format with the tab's unique ID as key.
        """
        self.notes[tab.tab_id] = tab.note_area.toPlainText()
        self.settings.setValue("notes/all", self.notes)


    def show_notes(self) -> None:
        """
        Toggle visibility of the notes panel in current tab.

        If no tab is active, does nothing. Toggles between visible
        and hidden states.
        """
        if tab := self.get_current_tab():
            tab.note_area.setVisible(not tab.note_area.isVisible())

    def toggle_pomodoro(self) -> None:
        """
        Control the Pomodoro productivity timer.

        When idle: Prompts for duration and starts countdown
        When running: Stops timer immediately
        Shows appropriate status messages to user.
        """
        if self.pomodoro_state == "idle":
            mins, ok = QInputDialog.getInt(
                self, "Pomodoro", "Minutes to focus:", 25, 1, 120
            )
            if ok:
                self.pomodoro_time = mins * 60
                self.pomodoro_state = "running"
                self.pomodoro_timer.start(1000)
                QMessageBox.information(
                    self, "Pomodoro", f"Focus timer started for {mins} minutes."
                )
            return
        self.pomodoro_timer.stop()
        self.pomodoro_state = "idle"
        QMessageBox.information(self, "Pomodoro", f"Timer stopped.")

    def pomodoro_tick(self) -> None:
        """
        Handle Pomodoro timer countdown logic.

        Decrements remaining time each second. When time expires:
        - Stops timer
        - Resets state
        - Notifies user
        """
        self.pomodoro_time -= 1
        if self.pomodoro_time <= 0:
            self.pomodoro_timer.stop()
            self.pomodoro_state = "idle"
            QMessageBox.information(self, "Pomodoro", "Time's up!")

    def screenshot(self) -> None:
        """
        Capture and saves screenshot of current tab.

        Prompts user for save location (default: screenshot.png).
        Shows success message or silently fails on error.
        If no tab is active, does nothing.
        """
        if tab := self.get_current_tab():
            pixmap = tab.webview.grab()
            img = pixmap.toImage()
            fname_tuple = QFileDialog.getSaveFileName(
                self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)"
            )
            fname = fname_tuple[0] if isinstance(fname_tuple, tuple) else fname_tuple
            if fname:
                img.save(fname)
                QMessageBox.information(self, "Screenshot", f"Saved as {fname}")

    def update_address_bar(self, qurl: Any, tab: BrowserTab) -> None:
        """
        Update address bar when a tab's URL changes.

        Args:
            qurl: The new QUrl object
            tab: The BrowserTab instance that changed

        Only updates if the changed tab is currently active.
        """
        if tab == self.get_current_tab():
            self.address_bar.setText(qurl.toString())

    def update_tab_title(self, title: str, idx: int) -> None:
        """
        Update a tab's displayed title.

        Args:
            title: The new title text
            idx: Tab index to update

        Uses "New Tab" if title is empty.
        """
        self.tabs.setTabText(
            idx,
            f"{title[:20]}..." if len(title) > 20 else title if title else "New Tab",
        )

    def set_tab_icon(self, idx: int, icon: Any) -> None:
        """
        Set favicon for a tab.

        Args:
            idx: Tab index to update
            icon: The QIcon to set

        Only sets if icon is valid (not null).
        """
        if not icon.isNull():
            self.tabs.setTabIcon(idx, icon)

    def handle_download(self, download):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", download.suggestedFileName()
        )

        if path:
            download.setPath(path)
            download.accept()
            download.finished.connect(self.on_download_finished)
        else:
            download.cancel()

    @staticmethod
    def on_download_finished(self):
        print("Загрузка завершена!")

    def save_history(self, qurl: Any, tab: Any) -> None:
        """
        Record visited URLs in browsing history.

        Args:
            qurl: The visited QUrl
            tab: The BrowserTab that loaded the URL

        Skips duplicate consecutive entries. Saves to disk after update.
        """
        url = qurl.toString()
        title = tab.webview.title() or url
        if url and (not self.history or self.history[-1]["url"] != url):
            self.history.append({"title": title, "url": url})
            save_json(HISTORY_FILE, self.history)

    def toggle_fullscreen(self) -> None:
        """
        Toggle browser window between normal and fullscreen states.

        Updates internal state flag to track current mode.
        """
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
            return

        self.showFullScreen()
        self.is_fullscreen = True

    def change_theme(self) -> None:
        """
        Toggle between light and dark theme modes.

        Delegates to apply_dark_mode using current settings.
        """
        mode = self.settings.value("mode/dark", type=bool)
        self.apply_dark_mode(mode)
        self.settings.setValue("mode/dark", not mode)

    def apply_dark_mode(self, enabled: bool) -> None:
        """
        Apply the selected theme stylesheet.

        Args:
            enabled: True for dark mode, False for light mode

        Updates application stylesheet and persists preference.
        """
        if enabled:
            self.parent_app.setStyleSheet(load_css(LIGHT_STYLE))
            self.navbar.actions()[0].setIcon(
                QIcon(self.create_path("arrow_left_light.png"))
            )
            self.navbar.actions()[1].setIcon(
                QIcon(self.create_path("arrow_right_light.png"))
            )
            self.navbar.actions()[2].setIcon(
                QIcon(self.create_path("refresh_light.png"))
            )
            self.navbar.actions()[3].setIcon(QIcon(self.create_path("home_light.png")))
            self.navbar.actions()[4].setIcon(
                QIcon(self.create_path("fullscreen_light.png"))
            )

            self.navbar.actions()[-1].setIcon(QIcon(self.create_path("dark_mode.png")))
            self.navbar.actions()[-2].setIcon(QIcon(self.create_path("camera.png")))
            self.navbar.actions()[-3].setIcon(QIcon(self.create_path("show_notes.png")))
            self.navbar.actions()[-4].setIcon(
                QIcon(self.create_path("clock_light.png"))
            )
        else:
            self.parent_app.setStyleSheet(load_css(DARK_STYLE))

            self.navbar.actions()[0].setIcon(
                QIcon(self.create_path("arrow_left_dark.png"))
            )
            self.navbar.actions()[1].setIcon(
                QIcon(self.create_path("arrow_right_dark.png"))
            )
            self.navbar.actions()[2].setIcon(
                QIcon(self.create_path("refresh_dark.png"))
            )
            self.navbar.actions()[3].setIcon(QIcon(self.create_path("home_dark.png")))
            self.navbar.actions()[4].setIcon(
                QIcon(self.create_path("fullscreen_dark.png"))
            )

            self.navbar.actions()[-1].setIcon(QIcon(self.create_path("light_mode.png")))
            self.navbar.actions()[-2].setIcon(QIcon(self.create_path("camera.png")))
            self.navbar.actions()[-3].setIcon(QIcon(self.create_path("show_notes.png")))
            self.navbar.actions()[-4].setIcon(QIcon(self.create_path("clock_dark.png")))

    def tab_context_menu(self, pos: QPoint) -> None:
        """
        Display context menu for tab management.

        Args:
            pos: Mouse position where menu was requested

        Shows menu with tab-specific actions:
        - Duplicate
        - Reload
        - Mute/Unmute
        - Close
        """
        idx = self.tabs.tabBar().tabAt(pos)
        if idx < 0:
            return
        menu = QMenu(self)
        duplicate_action = QAction("Duplicate Tab", self)
        duplicate_action.triggered.connect(
            lambda checked=False, i=idx: self.duplicate_tab(i)
        )
        reload_action = QAction("Reload Tab", self)
        reload_action.triggered.connect(lambda checked=False, i=idx: self.reload_tab(i))
        tab = self.tabs.widget(idx)
        page = tab.webview.page()
        mute_action = QAction(f"{"Unmute" if page.isAudioMuted() else "Mute"} Tab", self)
        mute_action.triggered.connect(
            lambda checked=False, i=idx: self.toggle_mute_tab(i)
        )
        close_action = QAction("Close Tab", self)
        close_action.triggered.connect(lambda checked=False, i=idx: self.close_tab(i))

        menu.addAction(duplicate_action)
        menu.addAction(reload_action)
        menu.addAction(mute_action)
        menu.addSeparator()
        menu.addAction(close_action)
        menu.exec(self.tabs.tabBar().mapToGlobal(pos))

    def duplicate_tab(self, idx: int) -> None:
        """
        Create new tab with same URL as specified tab.

        Args:
            idx: Index of tab to duplicate
        """
        if isinstance(tab := self.tabs.widget(idx), BrowserTab):
            url = tab.webview.url().toString()
            self.add_tab(url)

    def reload_tab(self, idx: int) -> None:
        """
        Reload webpage in specified tab.

        Args:
            idx: Index of tab to reload
        """
        if isinstance(tab := self.tabs.widget(idx), BrowserTab):
            tab.webview.reload()

    def toggle_mute_tab(self, idx: int) -> None:
        """
        Toggle audio mute state for specified tab.

        Args:
            idx: Index of tab to mute/unmute

        Shows current mute state in message box.
        """
        if isinstance(tab := self.tabs.widget(idx), BrowserTab):
            page = tab.webview.page()
            muted = page.isAudioMuted()
            page.setAudioMuted(not muted)

    def toggle_mute(self) -> None:
        """
        Toggle audio mute state for current tab.

        Shows current mute state in message box.
        If no tab is active, does nothing.
        """
        if tab := self.get_current_tab():
            page = tab.webview.page()
            muted = page.isAudioMuted()
            page.setAudioMuted(not muted)
            QMessageBox.information(
                self, "Mute", "Audio " + ("muted" if not muted else "unmuted")
            )
