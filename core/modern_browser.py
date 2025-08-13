from typing import Any

from PyQt6.QtCore import (
    QPoint,
    Qt,
    QTimer,
    QUrl
)
from PyQt6.QtGui import (
    QAction,
    QIcon
)
from PyQt6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QToolBar,
    QWidget
)

from browser_tab import BrowserTab
from config.config import (
    BOOKMARKS_FILE,
    HISTORY_FILE,
    HOME_URL,
    NOTES_FILE,
    SESSION_FILE,
    SETTINGS_FILE
)
from util import (
    save_json,
    load_json
)


class ModernBrowser(QMainWindow):
    def __init__(
            self) \
            -> None:
        super().__init__()
        self.setWindowTitle("Quilix Version 5.0 ENG")
        self.setGeometry(100, 100, 1400, 900)
        # --- State ---
        self.session = load_json(SESSION_FILE, [])
        self.bookmarks = load_json(BOOKMARKS_FILE, [])
        self.history = load_json(HISTORY_FILE, [])
        self.settings = load_json(SETTINGS_FILE, {"home_url": HOME_URL, "dark_mode": False})
        self.notes = load_json(NOTES_FILE, {})
        self.pomodoro_timer = QTimer(self)
        self.pomodoro_state = "idle"
        self.pomodoro_time = 0

        # --- UI ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_navbar)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self.tab_context_menu)
        self.setCentralWidget(self.tabs)

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        # Standard browser actions
        self.back_btn = QAction(QIcon.fromTheme("go-previous"), "←", self)
        self.back_btn.triggered.connect(self.go_back)
        self.navbar.addAction(self.back_btn)
        self.forward_btn = QAction(QIcon.fromTheme("go-next"), "→", self)
        self.forward_btn.triggered.connect(self.go_forward)
        self.navbar.addAction(self.forward_btn)
        self.reload_btn = QAction(QIcon.fromTheme("view-refresh"), "↺", self)
        self.reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(self.reload_btn)
        self.home_btn = QAction(QIcon.fromTheme("go-home"), "🏠", self)
        self.home_btn.triggered.connect(self.go_home)
        self.navbar.addAction(self.home_btn)
        self.fullscreen_btn = QAction(QIcon.fromTheme("view-fullscreen"), "⛶", self)
        self.fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.navbar.addAction(self.fullscreen_btn)
        self.navbar.addSeparator()

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Smart Search: url, bookmarks, actions (note, timer, mute, screenshot...)")
        self.address_bar.returnPressed.connect(self.smart_search)
        self.navbar.addWidget(self.address_bar)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(lambda: self.add_tab())
        self.navbar.addWidget(self.new_tab_btn)

        self.session_btn = QAction(QIcon.fromTheme("document-save"), "Save Session", self)
        self.session_btn.triggered.connect(self.save_session)
        self.navbar.addAction(self.session_btn)

        self.restore_btn = QAction(QIcon.fromTheme("document-open"), "Restore Session", self)
        self.restore_btn.triggered.connect(self.restore_session)
        self.navbar.addAction(self.restore_btn)

        self.notes_btn = QAction(QIcon.fromTheme("accessories-text-editor"), "Show Notes", self)
        self.notes_btn.triggered.connect(self.show_notes)
        self.navbar.addAction(self.notes_btn)

        self.pomodoro_btn = QAction(QIcon.fromTheme("clock"), "Pomodoro", self)
        self.pomodoro_btn.triggered.connect(self.toggle_pomodoro)
        self.navbar.addAction(self.pomodoro_btn)

        self.screenshot_btn = QAction(QIcon.fromTheme("camera-photo"), "Screenshot", self)
        self.screenshot_btn.triggered.connect(self.screenshot)
        self.navbar.addAction(self.screenshot_btn)

        self.is_fullscreen = False

        self.apply_dark_mode(self.settings.get("dark_mode", False))
        self.add_tab(url=self.settings.get("home_url", HOME_URL))

        self.pomodoro_timer.timeout.connect(self.pomodoro_tick)

    def add_tab(
            self,
            url: str | None = None) \
            -> None:
        url = url or self.settings.get("home_url", HOME_URL)
        tab = BrowserTab(url=url)
        idx = self.tabs.addTab(tab, "New Tab")
        tab.webview.urlChanged.connect(lambda qurl, t=tab: self.update_address_bar(qurl, t))
        tab.webview.titleChanged.connect(lambda title, i=idx: self.update_tab_title(title, i))
        tab.webview.iconChanged.connect(lambda icon, i=idx: self.set_tab_icon(i, icon))
        tab.webview.urlChanged.connect(lambda qurl, t=tab: self.save_history(qurl, t))
        tab.note_area.textChanged.connect(lambda t=tab: self.save_note(t))
        if tab.tab_id in self.notes:
            tab.note_area.setText(self.notes[tab.tab_id])
        self.tabs.setCurrentIndex(idx)

    def close_tab(
            self,
            idx: int) \
            -> None:
        if self.tabs.count() > 1:
            self.tabs.removeTab(idx)
        else:
            tab = self.tabs.widget(idx)
            if isinstance(tab, BrowserTab):
                tab.webview.setUrl(QUrl(self.settings.get("home_url", HOME_URL)))

    def update_navbar(
            self,
            idx: int) \
            -> None:
        current_tab = self.get_current_tab()
        if current_tab:
            self.address_bar.setText(current_tab.webview.url().toString())

    def get_current_tab(
            self) \
            -> QWidget | None:
        tab = self.tabs.currentWidget()
        return tab if isinstance(tab, BrowserTab) else None

    def go_back(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.webview.back()

    def go_forward(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.webview.forward()

    def reload_page(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.webview.reload()

    def go_home(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.webview.setUrl(QUrl(self.settings.get("home_url", HOME_URL)))

    def smart_search(
            self) \
            -> None:
        text = self.address_bar.text().strip()
        if not text:
            return
        if text.lower() == "note":
            self.show_notes()
            return
        elif text.lower().startswith("timer"):
            self.toggle_pomodoro()
            return
        elif text.lower() == "mute":
            self.toggle_mute()
            return
        elif text.lower() == "screenshot":
            self.screenshot()
            return
        for b in self.bookmarks:
            if text.lower() in b["title"].lower() or text.lower() in b["url"].lower():
                self.add_tab(b["url"])
                return
        for h in reversed(self.history):
            if text.lower() in h["title"].lower() or text.lower() in h["url"].lower():
                self.add_tab(h["url"])
                return
        if "." in text or text.startswith("http"):
            url = text if text.startswith("http") else "https://" + text
            self.add_tab(url)
        else:
            self.add_tab("https://www.google.com/search?q=" + text)

    def save_session(
            self) \
            -> None:
        session = [tab := self.tabs.widget(i) for i in range(self.tabs.count()) if isinstance(tab, BrowserTab)]
        save_json(SESSION_FILE, session)
        QMessageBox.information(self, "Session", "Session saved!")

    def restore_session(
            self) \
            -> None:
        self.tabs.clear()
        self.session = load_json(SESSION_FILE, [])
        for t in self.session:
            self.add_tab(t["url"])

    def save_note(
            self,
            tab: BrowserTab) \
            -> None:
        self.notes[tab.tab_id] = tab.note_area.toPlainText()
        save_json(NOTES_FILE, self.notes)

    def show_notes(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.note_area.setVisible(not tab.note_area.isVisible())

    def toggle_pomodoro(
            self) \
            -> None:
        if self.pomodoro_state == "idle":
            mins, ok = QInputDialog.getInt(self, "Pomodoro", "Minutes to focus:", 25, 1, 120)
            if ok:
                self.pomodoro_time = mins * 60
                self.pomodoro_state = "running"
                self.pomodoro_timer.start(1000)
                QMessageBox.information(self, "Pomodoro", f"Focus timer started for {mins} minutes.")
        else:
            self.pomodoro_timer.stop()
            self.pomodoro_state = "idle"
            QMessageBox.information(self, "Pomodoro", f"Timer stopped.")

    def pomodoro_tick(
            self) \
            -> None:
        self.pomodoro_time -= 1
        if self.pomodoro_time <= 0:
            self.pomodoro_timer.stop()
            self.pomodoro_state = "idle"
            QMessageBox.information(self, "Pomodoro", "Time's up!")

    def screenshot(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            pixmap = tab.webview.grab()
            img = pixmap.toImage()
            fname_tuple = QFileDialog.getSaveFileName(self, "Save Screenshot", "screenshot.png", "PNG Files (*.png)")
            fname = fname_tuple[0] if isinstance(fname_tuple, tuple) else fname_tuple
            if fname:
                img.save(fname)
                QMessageBox.information(self, "Screenshot", f"Saved as {fname}")

    def update_address_bar(
            self,
            qurl: Any,
            tab: BrowserTab) \
            -> None:
        if tab == self.get_current_tab():
            self.address_bar.setText(qurl.toString())

    def update_tab_title(
            self,
            title: str,
            idx: int) \
            -> None:
        self.tabs.setTabText(idx, title if title else "New Tab")

    def set_tab_icon(
            self,
            idx: int,
            icon: Any) \
            -> None:
        if not icon.isNull():
            self.tabs.setTabIcon(idx, icon)

    def save_history(
            self,
            qurl: Any,
            tab: Any) \
            -> None:
        url = qurl.toString()
        title = tab.webview.title() or url
        if url and (not self.history or self.history[-1]["url"] != url):
            self.history.append({"title": title, "url": url})
            save_json(HISTORY_FILE, self.history)

    def toggle_fullscreen(
            self) \
            -> None:
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def apply_dark_mode(
            self,
            enabled: bool) \
            -> None:
        if enabled:
            self.setStyleSheet("""QMainWindow, QWidget, QTabWidget, QToolBar, QLineEdit, QListWidget, QDialog, QLabel, QPushButton {
                    background-color: #222 !important;
                    color: #eee !important;
                }
                QLineEdit, QListWidget {
                    background-color: #333 !important;
                    color: #eee !important;
                }
            """)
        else:
            self.setStyleSheet("")

    def tab_context_menu(
            self,
            pos: QPoint) \
            -> None:
        idx = self.tabs.tabBar().tabAt(pos)
        if idx < 0:
            return
        menu = QMenu(self)
        duplicate_action = QAction("Duplicate Tab", self)
        duplicate_action.triggered.connect(lambda checked=False, i=idx: self.duplicate_tab(i))
        reload_action = QAction("Reload Tab", self)
        reload_action.triggered.connect(lambda checked=False, i=idx: self.reload_tab(i))
        mute_action = QAction("Mute/Unmute Tab", self)
        mute_action.triggered.connect(lambda checked=False, i=idx: self.toggle_mute_tab(i))
        close_action = QAction("Close Tab", self)
        close_action.triggered.connect(lambda checked=False, i=idx: self.close_tab(i))

        menu.addAction(duplicate_action)
        menu.addAction(reload_action)
        menu.addAction(mute_action)
        menu.addSeparator()
        menu.addAction(close_action)
        menu.exec(self.tabs.tabBar().mapToGlobal(pos))

    def duplicate_tab(
            self,
            idx: int) \
            -> None:
        tab = self.tabs.widget(idx)
        if isinstance(tab, BrowserTab):
            url = tab.webview.url().toString()
            self.add_tab(url)

    def reload_tab(
            self,
            idx: int) \
            -> None:
        tab = self.tabs.widget(idx)
        if isinstance(tab, BrowserTab):
            tab.webview.reload()

    def toggle_mute_tab(
            self,
            idx: int) \
            -> None:
        tab = self.tabs.widget(idx)
        if isinstance(tab, BrowserTab):
            page = tab.webview.page()
            muted = page.isAudioMuted()
            page.setAudioMuted(not muted)
            QMessageBox.information(self, "Mute", "Audio " + ("muted" if not muted else "unmuted"))

    def toggle_mute(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            page = tab.webview.page()
            muted = page.isAudioMuted()
            page.setAudioMuted(not muted)
            QMessageBox.information(self, "Mute", "Audio " + ("muted" if not muted else "unmuted"))
