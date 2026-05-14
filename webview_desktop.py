from webview_console import launch
from webview_console.multiprocessing_bootstrap import configure_multiprocessing


if __name__ == "__main__":
    configure_multiprocessing()
    launch()
