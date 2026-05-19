from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from .bridge import Bridge
from .infra.config_store import ConfigStore
from .infra.event_pusher import EventPusher
from app_metadata import APP_TITLE
from .paths import app_storage_dir, config_path, frontend_dist_dir
from .runtime import Runtime

DEFAULT_WINDOW_WIDTH = 1540
DEFAULT_WINDOW_HEIGHT = 980
DEFAULT_MIN_WINDOW_SIZE = (1280, 820)
DEFAULT_DEV_SERVER_CANDIDATES = (
    "http://127.0.0.1:5173/",
    "http://localhost:5173/",
)
DEFAULT_HTTP_TIMEOUT_SECONDS = 0.75


@dataclass(frozen=True)
class WindowSpec:
    width: int
    height: int
    min_size: tuple[int, int]
    maximized: bool = False


def _normalize_url(raw_url: str) -> str:
    url = raw_url.strip()
    if not url:
        return ""
    if not url.endswith("/"):
        url = f"{url}/"
    return url


def _url_is_alive(url: str) -> bool:
    request = Request(
        url,
        headers={
            "User-Agent": "AnnualReportWorkbenchDesktop/1.0",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urlopen(request, timeout=DEFAULT_HTTP_TIMEOUT_SECONDS) as response:
            return 200 <= getattr(response, "status", 200) < 400
    except (OSError, URLError, ValueError):
        return False


def _candidate_frontend_urls() -> list[str]:
    manual = _normalize_url(os.environ.get("ARW_WEBUI_URL", ""))
    candidates = [manual] if manual else []
    candidates.extend(DEFAULT_DEV_SERVER_CANDIDATES)
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            deduped.append(candidate)
    return deduped


def resolve_frontend_entry() -> str:
    mode = os.environ.get("ARW_WEBUI_SOURCE", "auto").strip().lower() or "auto"

    frontend_index = frontend_dist_dir() / "index.html"
    if mode == "auto" and frontend_index.exists():
        return frontend_index.as_uri()

    if mode == "dev":
        for candidate in _candidate_frontend_urls():
            if _url_is_alive(candidate):
                return candidate
        raise FileNotFoundError("Frontend dev server is not reachable. Set ARW_WEBUI_URL or start the Vite dev server.")

    if frontend_index.exists():
        return frontend_index.as_uri()

    if mode == "auto":
        for candidate in _candidate_frontend_urls():
            if _url_is_alive(candidate):
                return candidate
        raise FileNotFoundError(f"Frontend build not found and no dev server is reachable: {frontend_index}")

    raise FileNotFoundError(f"Frontend build not found: {frontend_index}")


def _read_windows_work_area() -> tuple[int, int] | None:
    if os.name != "nt":
        return None

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    if not ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
        return None
    return rect.right - rect.left, rect.bottom - rect.top


def resolve_window_spec() -> WindowSpec:
    min_width, min_height = DEFAULT_MIN_WINDOW_SIZE
    work_area = _read_windows_work_area()
    if work_area is None:
        return WindowSpec(
            width=DEFAULT_WINDOW_WIDTH,
            height=DEFAULT_WINDOW_HEIGHT,
            min_size=DEFAULT_MIN_WINDOW_SIZE,
        )

    work_width, work_height = work_area
    if work_width < min_width or work_height < min_height:
        return WindowSpec(
            width=work_width,
            height=work_height,
            min_size=(work_width, work_height),
            maximized=True,
        )

    width = min(DEFAULT_WINDOW_WIDTH, work_width)
    height = min(DEFAULT_WINDOW_HEIGHT, work_height)
    width = max(min_width, width)
    height = max(min_height, height)

    maximize = bool(work_width <= DEFAULT_WINDOW_WIDTH or work_height <= DEFAULT_WINDOW_HEIGHT)
    return WindowSpec(
        width=width,
        height=height,
        min_size=DEFAULT_MIN_WINDOW_SIZE,
        maximized=maximize,
    )


def launch() -> None:
    try:
        import webview
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("pywebview is required. Install dependencies from webview_console/requirements.txt") from exc

    frontend_entry = resolve_frontend_entry()
    window_spec = resolve_window_spec()

    config_store = ConfigStore(config_path())
    event_pusher = EventPusher()
    runtime = Runtime(config_store, event_pusher)
    bridge = Bridge(runtime)

    window = webview.create_window(
        title=APP_TITLE,
        url=frontend_entry,
        js_api=bridge,
        width=window_spec.width,
        height=window_spec.height,
        min_size=window_spec.min_size,
        maximized=window_spec.maximized,
        text_select=True,
        zoomable=True,
    )
    runtime.attach_window(window)

    def _on_closing():
        return runtime.request_window_close()

    try:
        window.events.closing += _on_closing
    except Exception:
        pass

    storage_dir = app_storage_dir() / "webview-profile"
    storage_dir.mkdir(parents=True, exist_ok=True)

    webview.start(
        debug=os.environ.get("ARW_WEBVIEW_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"},
        gui="edgechromium" if os.name == "nt" else None,
        private_mode=False,
        storage_path=str(storage_dir),
    )
