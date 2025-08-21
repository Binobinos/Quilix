"""Application configuration constants.

This module contains all the default configuration values used throughout
the Quilix browser application including URLs, file paths, version information,
and Qt WebEngine flags.
"""

PAGE_URL = "home//main.html"
"""str: The default homepage URL that loads when the browser starts."""

HOME_URL = "https://google.com"
"""str: The default search engine"""

ICON_DIR = "icons"
"""str: Directory name where browser icon files are stored"""

STYLE_DIR = "styles"
"""str: Directory name containing CSS style sheets for the application."""

DARK_STYLE = "dark_mode.css"
"""str: Path to the dark mode stylesheet."""

LIGHT_STYLE = "light_mode.css"
"""str: Path to the light mode stylesheet."""

__version__ = "Quilix Version 1.0.0 ENG"
"""str: The current version string of the Quilix browser."""

FLAGS = {
    "QT_STYLE_OVERRIDE": "",
    "QTWEBENGINE_REMOTE_DEBUGGING": "9222",
    "QTWEBENGINE_CHROMIUM_FLAGS": (
        "--no-sandbox --remote-allow-origins=* --enable-devtools-experiments"
    ),
    "QT_QPA_PLATFORMTHEME": "",
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
