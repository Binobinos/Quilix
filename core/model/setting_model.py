from typing import Literal, TypedDict


class ItemHistory(TypedDict):
    title: str
    url: str


class SizeWindow(TypedDict):
    x: int
    y: int
    width: int
    height: int


class Setting(TypedDict):
    language: str
    theme: str
    home_page: Literal["last", "custom", "new"]
    home_url: str
    history: list[ItemHistory]
    size_window: SizeWindow
    last_session: list[ItemHistory]
