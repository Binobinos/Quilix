"""Application configuration constants.

This module contains all the default configuration values used throughout
the Quilix browser application including URLs, file paths, version information,
and Qt WebEngine flags.
"""

HOME_URL = "https://www.google.com"
"""str: The default homepage URL that loads when the browser starts."""

CACHE_DIR = "cache"
"""str: Directory name where browser cache files are stored."""

STYLE_DIR = "styles"
"""str: Directory name containing CSS style sheets for the application."""

BOOKMARKS_FILE = "quilix_bookmarks.json"
"""str: Filename for storing browser bookmarks in JSON format."""

HISTORY_FILE = "quilix_history.json"
"""str: Filename for storing browsing history in JSON format."""

SETTINGS_FILE = "quilix_settings.json"
"""str: Filename for storing application settings in JSON format."""

SESSION_FILE = "quilix_session.json"
"""str: Filename for storing session data in JSON format."""

NOTES_FILE = "quilix_notes.json"
"""str: Filename for storing user notes in JSON format."""

DARK_STYLE = "styles//dark_mode.css"
"""str: Path to the dark mode stylesheet."""

LIGHT_STYLE = "styles//light_mode.css"
"""str: Path to the light mode stylesheet."""

__version__ = "Quilix Version 7.0.0M ENG"
"""str: The current version string of the Quilix browser."""

FLAGS = {
    "QT_STYLE_OVERRIDE": "",
    "QTWEBENGINE_REMOTE_DEBUGGING": "9222",
    "QTWEBENGINE_CHROMIUM_FLAGS": (
        '--no-sandbox '
        '--remote-allow-origins=* '
        '--enable-devtools-experiments'
    ),
    "QT_QPA_PLATFORMTHEME": ""
}
"""dict: Qt WebEngine configuration flags.

The flags control various aspects of the browser engine behavior:

- `QT_STYLE_OVERRIDE`: Custom Qt style override (empty for default)
- `QTWEBENGINE_REMOTE_DEBUGGING`: Enables remote debugging on port 9222
- `QTWEBENGINE_CHROMIUM_FLAGS`: Chromium-specific flags including:
  - `--no-sandbox`: Disables Chromium sandbox (security trade-off)
  - `--remote-allow-origins=*`: Allows remote connections from any origin
  - `--enable-devtools-experiments`: Enables experimental devtools features
- `QT_QPA_PLATFORMTHEME`: Platform theme override (empty for default)
"""
