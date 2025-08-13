import json
import os
from typing import Any


def load_json(
        filename: str,
        default: list[Any] | dict[str, str]) \
        -> list[dict[str, str]]:
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def create_dir(path_dir: str, file_name: str) -> str:
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
    return os.path.join(path_dir, file_name)


def save_json(
        filename: str,
        content: list[Any] | dict[str, Any]) \
        -> None:
    try:
        with open(filename, "w") as f:
            json.dump(content, f)
    except Exception:
        pass

def load_css(filename) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
