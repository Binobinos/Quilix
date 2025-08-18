"""
JSON and file utility functions.

This module provides utility functions for working with JSON files, directories,
and CSS files.
"""

import json
import os
from typing import (
    Any,
    LiteralString, TypeVar
)

from model.setting_model import Setting

T = TypeVar("T", list[Any], dict[str, str])


def load_json(
        filename: str,
        default: list[Any] | dict[str, str]) \
        -> list[dict[str, str]] | dict[str, str] | T:
    """
    Load JSON data from a file, returning a default value if the file doesn't exist or is invalid.

    Args:
        filename: Path to the JSON file to load.
        default: Default value to return if the file doesn't exist or can't be parsed.

    Returns:
        The parsed JSON data (as a list or dictionary) if successful, otherwise the default value.

    Example:
        >>> data = load_json('config.json', {'default': 'value'})
        >>> print(data)
        {'actual': 'config'}  # or {'default': 'value'} if file doesn't exist
    """
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return default


def create_dir(
        path_dir: str,
        file_name: str) \
        -> LiteralString:
    """
    Create a directory if it doesn't exist and returns a joined path.

    If the specified directory doesn't exist, this function will create it before
    joining it with the given filename.

    Args:
        path_dir: Directory path to create (if needed) and join with filename.
        file_name: Filename to join with the directory path.

    Returns:
        The joined path combining the directory and filename.

    Example:
        >>> path = create_dir('data', 'config.json')
        >>> print(path)
        'data/config.json'
    """
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
    return os.path.join(path_dir, file_name)


def save_json(
        filename: str,
        content: list[Any] | dict[str, Any]) \
        -> None:
    """
    Save content to a JSON file, silently failing on error.

    This function attempts to write the given content to a JSON file. If any
    error occurs during writing, it will fail silently without raising an
    exception.

    Args:
        filename: Path to the file where content should be saved.
        content: Data to save (either a list or dictionary).

    Example:
        >>> save_json('data.json', {'key': 'value'})
    """
    try:
        with open(filename, "w") as f:
            json.dump(content, f)
    except Exception as e:
        print(e)


def load_css(
        filename: str) \
        -> str:
    """
    Read and returns the contents of a CSS file.

    Args:
        filename: Path to the CSS file to read.

    Returns:
        The contents of the CSS file as a string.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        UnicodeDecodeError: If there's an encoding error reading the file.

    Example:
        >>> css = load_css('styles.css')
        >>> print(css[:50])
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def generate_setting(setting_path: str) -> Setting:
    setting = {

    }
    return


def load_setting(setting_path: str) -> Setting:
    pass


def save_setting(new_setting: Setting, setting_path: str) -> None:
    pass
