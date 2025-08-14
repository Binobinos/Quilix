import os
import sys
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
    QApplication,
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
    CACHE_DIR,
    STYLE_DIR,
    ICON_DIR,
    SETTINGS_FILE,
    DARK_STYLE,
    LIGHT_STYLE,
    __version__
)
from util import (
    load_json,
    save_json,
    create_dir,
    load_css
)


class ModernBrowser(QMainWindow):
    def __init__(
            self, 
            app) \
            -> None:
        super().__init__()
        self.setWindowTitle(__version__)
        self.setGeometry(100, 100, 1400, 900)

        # --- State ---
        self.parent_app = app
        self.create_path = lambda path: create_dir(CACHE_DIR, path)

        self.session = load_json(self.create_path(SESSION_FILE), [])
        self.bookmarks = load_json(self.create_path(BOOKMARKS_FILE), [])
        self.history = load_json(self.create_path(HISTORY_FILE), [])
        self.settings = load_json(self.create_path(SETTINGS_FILE), {"home_url": HOME_URL, "dark_mode": False})
        self.notes = load_json(self.create_path(NOTES_FILE), {})
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

        """Standard browser actions (buttons back forward home and fullscreen)"""
        self.create_path = lambda path: create_dir(ICON_DIR, path)
        self.back_btn = QAction(QIcon(self.create_path("arrow_left_dark.png")), "←", self)
        self.back_btn.triggered.connect(self.go_back)
        self.navbar.addAction(self.back_btn)
        self.forward_btn = QAction(QIcon.fromTheme("go-next"), "→", self)
        self.forward_btn.triggered.connect(self.go_forward)
        self.navbar.addAction(self.forward_btn)
        self.reload_btn = QAction(QIcon(self.create_path("refresh_dark.png")), "↺", self)
        self.reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(self.reload_btn)
        self.home_btn = QAction(QIcon(self.create_path("home_dark.png")), "🏠", self)
        self.home_btn.triggered.connect(self.go_home)
        self.navbar.addAction(self.home_btn)
        self.fullscreen_btn = QAction(QIcon(self.create_path("fullscreen_dark")), "⛶", self)
        self.fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.navbar.addAction(self.fullscreen_btn)
        self.navbar.addSeparator()
        """Adress bar"""
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Smart Search: url, bookmarks, actions (note, timer, mute, screenshot...)")
        self.address_bar.returnPressed.connect(self.smart_search)
        self.navbar.addWidget(self.address_bar)
        """New tab button"""
        self.new_tab_btn = QAction(QIcon(self.create_path("add_dark.png")), "New Tab", self)
        self.new_tab_btn.triggered.connect(lambda: self.add_tab())
        self.navbar.addAction(self.new_tab_btn)
        """Pomodoro (timer)"""
        self.pomodoro_btn = QAction(QIcon(self.create_path("clock_dark.png")), "Pomodoro", self)
        self.pomodoro_btn.triggered.connect(self.toggle_pomodoro)
        self.navbar.addAction(self.pomodoro_btn)
        """Saving session button"""
        self.session_btn = QAction(QIcon(self.create_path("document_save.png")), "Save Session", self)
        self.session_btn.triggered.connect(self.save_session)
        self.navbar.addAction(self.session_btn)
        """Restoring session button"""
        self.restore_btn = QAction(QIcon(self.create_path("document_open.png")), "Restore Session", self)
        self.restore_btn.triggered.connect(self.restore_session)
        self.navbar.addAction(self.restore_btn)
        """Notes Button"""
        self.notes_btn = QAction(QIcon(self.create_path("show_notes.png")), "Show Notes", self)
        self.notes_btn.triggered.connect(self.show_notes)
        self.navbar.addAction(self.notes_btn)
        """Screenshot Button"""
        self.screenshot_btn = QAction(QIcon(self.create_path("camera.png")), "Screenshot", self)
        self.screenshot_btn.triggered.connect(self.screenshot)
        self.navbar.addAction(self.screenshot_btn)
        """Light and dark mode button"""
        self.change_theme_btn = QAction(QIcon(self.create_path("light_mode.png")), "Change Theme", self)
        self.change_theme_btn.triggered.connect(self.change_theme)
        self.navbar.addAction(self.change_theme_btn)

        self.is_fullscreen = False

        self.change_theme()
        self.add_tab(url=self.settings.get("home_url", HOME_URL))

        self.pomodoro_timer.timeout.connect(self.pomodoro_tick)
    """Adding new tab button"""
    def add_tab(
            self,
            url: str | None = None) \
            -> None:
        url = url or self.settings.get("home_url", HOME_URL)
        tab = BrowserTab(self, url=url)
        idx = self.tabs.addTab(tab, "New Tab")
        tab.webview.urlChanged.connect(lambda qurl, t=tab: self.update_address_bar(qurl, t))
        tab.webview.titleChanged.connect(lambda title, i=idx: self.update_tab_title(title, i))
        tab.webview.iconChanged.connect(lambda icon, i=idx: self.set_tab_icon(i, icon))
        tab.webview.urlChanged.connect(lambda qurl, t=tab: self.save_history(qurl, t))
        tab.note_area.textChanged.connect(lambda t=tab: self.save_note(t))
        if tab.tab_id in self.notes:
            tab.note_area.setText(self.notes[tab.tab_id])
        self.tabs.setCurrentIndex(idx)
    """Closisng tab button"""
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
    """NavBar engine"""
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
    """Buttons engine"""
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
    """Save session button engine"""
    def save_session(
            self) \
            -> None:
        try:
            session = [{"url": tab.webview.url().toString()} for i in range(self.tabs.count()) if
                       isinstance((tab := self.tabs.widget(i)), BrowserTab)]
            save_json(SESSION_FILE, session)
            QMessageBox.information(self, "Session", "Session saved!")
        except Exception as e:
            print(e)
    """Restore session engine"""
    def restore_session(
            self) \
            -> None:
        self.tabs.clear()
        self.session = load_json(self.create_path(SESSION_FILE), [])
        for t in self.session:
            print(t)
            self.add_tab(t["url"])
    """Save note engine"""
    def save_note(
            self,
            tab: BrowserTab) \
            -> None:
        self.notes[tab.tab_id] = tab.note_area.toPlainText()
        save_json(NOTES_FILE, self.notes)
    """Show notes engine"""
    def show_notes(
            self) \
            -> None:
        tab = self.get_current_tab()
        if tab:
            tab.note_area.setVisible(not tab.note_area.isVisible())
    """Pomodoro engine"""
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
    """Screenshot engine"""
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
    """Updating address bar engine"""
    def update_address_bar(
            self,
            qurl: Any,
            tab: BrowserTab) \
            -> None:
        if tab == self.get_current_tab():
            self.address_bar.setText(qurl.toString())
    """Update tab engine"""
    def update_tab_title(
            self,
            title: str,
            idx: int) \
            -> None:
        self.tabs.setTabText(idx, title if title else "New Tab")
    """Set tab icon engine"""
    def set_tab_icon(
            self,
            idx: int,
            icon: Any) \
            -> None:
        if not icon.isNull():
            self.tabs.setTabIcon(idx, icon)
    """Save history engine"""
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
    """Fullscreen engine"""
    def toggle_fullscreen(
            self) \
            -> None:
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
    """Change theme engine"""
    def change_theme(self) -> None:
        self.apply_dark_mode(self.settings.get("dark_mode"))

    def apply_dark_mode(
            self,
            enabled: bool) \
            -> None:
        if enabled:
            self.create_path = lambda path: create_dir(STYLE_DIR, path)
            self.parent_app.setStyleSheet(load_css(self.create_path(DARK_STYLE)))

            self.create_path = lambda path: create_dir(ICON_DIR, path)
            self.back_btn.setIcon(QIcon(self.create_path("arrow_left_light.png")))
            self.forward_btn.setIcon(QIcon(self.create_path("arrow_right_light.png")))
            self.reload_btn.setIcon(QIcon(self.create_path("refresh_light.png")))
            self.home_btn.setIcon(QIcon(self.create_path("home_light.png")))
            self.fullscreen_btn.setIcon(QIcon(self.create_path("fullscreen_light.png")))

            self.new_tab_btn.setIcon(QIcon(self.create_path("add_light.png")))
            self.change_theme_btn.setIcon(QIcon(self.create_path("dark_mode.png")))
            self.pomodoro_btn.setIcon(QIcon(self.create_path("clock_light.png")))

            self.settings["dark_mode"] = not enabled
        else:
            self.create_path = lambda path: create_dir(STYLE_DIR, path)
            self.parent_app.setStyleSheet(load_css(self.create_path(LIGHT_STYLE)))

            self.create_path = lambda path: create_dir(ICON_DIR, path)
            self.back_btn.setIcon(QIcon(self.create_path("arrow_left_dark.png")))
            self.forward_btn.setIcon(QIcon(self.create_path("arrow_right_dark.png")))
            self.reload_btn.setIcon(QIcon(self.create_path("refresh_dark.png")))
            self.home_btn.setIcon(QIcon(self.create_path("home_dark.png")))
            self.fullscreen_btn.setIcon(QIcon(self.create_path("fullscreen_dark.png")))

            self.new_tab_btn.setIcon(QIcon(self.create_path("add_dark.png")))
            self.change_theme_btn.setIcon(QIcon(self.create_path("light_mode.png")))
            self.pomodoro_btn.setIcon(QIcon(self.create_path("clock_dark.png")))

            self.settings["dark_mode"] = not enabled
    """Contex menu engine"""
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




if __name__ == "__main__":
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox'
    app = QApplication(sys.argv)
    browser = ModernBrowser()
    browser.show()
    sys.exit(app.exec())
