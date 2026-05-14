from .launcher import launch
from .multiprocessing_bootstrap import configure_multiprocessing


if __name__ == "__main__":
    configure_multiprocessing()
    launch()
