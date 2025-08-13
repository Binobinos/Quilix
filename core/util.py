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


def save_json(
        filename: str,
        content: list[Any] | dict[str, Any]) \
        -> None:
    try:
        with open(filename, "w") as f:
            json.dump(content, f)
    except Exception:
        pass
