import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
LOG_DIRECTORY = os.getenv("LOGGER_LOG_DIR", "logs")
LOG_FILENAME = os.getenv("LOGGER_FILENAME", "app.log")

# loggeer constants
LOG_FORMAT = "%(asctime)s [%(levelname)s] - %(pathname)s | %(funcName)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_NAME = 'app_logger'

# Create logs directory if it doesn't exist
log_dir = Path(LOG_DIRECTORY)
log_dir.mkdir(exist_ok=True)
log_file_path = log_dir / LOG_FILENAME

logger = logging.getLogger(LOGGER_NAME)
# set the default log level
logger.setLevel(logging.INFO)

# create formatter and add it to the handler
formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

# create handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(log_file_path)

# set format to handlers
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add handlers to the logger
logger.handlers = [stream_handler, file_handler]
