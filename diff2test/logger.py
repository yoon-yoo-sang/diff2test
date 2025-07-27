import logging
from rich.logging import RichHandler


logger = logging.getLogger("diff2test")

logger.setLevel(logging.DEBUG)

if not logger.handlers:
    rich_handler = RichHandler(
        show_path=False,
        show_level=True,
        show_time=False,
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)

logger.propagate = False
