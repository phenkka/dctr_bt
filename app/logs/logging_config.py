import logging

logging.basicConfig(
    level=logging.INFO,
    filename="app/logs/bot.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("bot_logger")