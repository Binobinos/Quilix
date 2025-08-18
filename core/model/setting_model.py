from typing import (
    TypedDict,
    Literal,
    NotRequired,
    Required
)


class ItemHistory(TypedDict):
    title: str
    url: str


class SizeWindow(TypedDict):
    x: int
    y: int
    width: int
    height: int


class Setting(TypedDict):
    language: NotRequired[Literal["ru", "eng"]]
    is_fullscreen: bool
    theme: Literal["dark", "light"]
    dark_mode: bool
    home_url: str
    size_window: Required[SizeWindow]
    history: NotRequired[list[ItemHistory]]
    notes: NotRequired[dict[str, str]]
    last_session: NotRequired[list[ItemHistory]]
    last_session_index: NotRequired[int]
    pomodoro_state: NotRequired[Literal["idle", "running"]]
    pomodoro_time: NotRequired[int]
