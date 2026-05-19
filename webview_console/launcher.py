from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from .bridge import Bridge
from . import events
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

WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
GWL_STYLE = -16
HTCLIENT = 1
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00080000
WS_POPUP = 0x80000000


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


def patch_native_resize_support() -> None:
    if os.name != "nt":
        return

    try:
        import webview.platforms.winforms as winforms
        from System import IntPtr
        from System.Drawing import Point
        import System.Windows.Forms as WinForms
    except Exception:
        return

    if getattr(winforms, "_arw_native_resize_patched", False):
        return

    def _signed_word(value: int) -> int:
        return ctypes.c_short(value & 0xFFFF).value

    def _apply_native_frame_style(form) -> None:
        try:
            hwnd = form.Handle.ToInt32()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style |= WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU
            style &= ~WS_CAPTION
            style &= ~WS_POPUP
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            ctypes.windll.user32.SetWindowPos(
                hwnd,
                None,
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
            )
        except Exception:
            pass

    class ResizeNativeWindow(WinForms.NativeWindow):
        def __init__(self, form):
            super().__init__()
            self._form = form
            self.AssignHandle(form.Handle)

        def WndProc(self, m):  # type: ignore[override]
            message = int(m.Msg)
            if message == WM_NCCALCSIZE and int(m.WParam.ToInt64()) != 0:
                m.Result = IntPtr.Zero
                return

            if message == WM_NCHITTEST and self._form.WindowState != WinForms.FormWindowState.Maximized:
                lparam = int(m.LParam.ToInt64()) & 0xFFFFFFFFFFFFFFFF
                screen_x = _signed_word(lparam)
                screen_y = _signed_word((lparam >> 16) & 0xFFFF)
                screen_point = Point(screen_x, screen_y)
                client_point = self._form.PointToClient(screen_point)
                border = 8
                width = int(self._form.ClientSize.Width)
                height = int(self._form.ClientSize.Height)

                left = client_point.X < border
                right = client_point.X >= max(0, width - border)
                top = client_point.Y < border
                bottom = client_point.Y >= max(0, height - border)

                if top and left:
                    m.Result = IntPtr(HTTOPLEFT)
                    return
                if top and right:
                    m.Result = IntPtr(HTTOPRIGHT)
                    return
                if bottom and left:
                    m.Result = IntPtr(HTBOTTOMLEFT)
                    return
                if bottom and right:
                    m.Result = IntPtr(HTBOTTOMRIGHT)
                    return
                if left:
                    m.Result = IntPtr(HTLEFT)
                    return
                if right:
                    m.Result = IntPtr(HTRIGHT)
                    return
                if top:
                    m.Result = IntPtr(HTTOP)
                    return
                if bottom:
                    m.Result = IntPtr(HTBOTTOM)
                    return

                m.Result = IntPtr(HTCLIENT)
                return

            super().WndProc(m)

    def _attach_resize_window(form):
        try:
            _apply_native_frame_style(form)
            form._arw_resize_native_window = ResizeNativeWindow(form)
        except Exception:
            pass

    original_on_shown = winforms.BrowserView.BrowserForm.on_shown

    def _on_shown(self, *_):
        _attach_resize_window(self)
        return original_on_shown(self, *_)

    winforms.BrowserView.BrowserForm.on_shown = _on_shown

    original_on_close = winforms.BrowserView.BrowserForm.on_close

    def _on_close(self, *_):
        try:
            native_window = getattr(self, "_arw_resize_native_window", None)
            if native_window is not None:
                native_window.ReleaseHandle()
        except Exception:
            pass
        return original_on_close(self, *_)

    winforms.BrowserView.BrowserForm.on_close = _on_close
    winforms._arw_native_resize_patched = True


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
        frameless=False,
        easy_drag=False,
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

    try:
        window.events.minimized += lambda: runtime.emit(events.window_state_changed("minimized"))
        window.events.maximized += lambda: runtime.emit(events.window_state_changed("maximized"))
        window.events.restored += lambda: runtime.emit(events.window_state_changed("normal"))
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
