import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
LOGDIR = os.getenv("LOGDIR", "logs")
LOGFILE_NAME = os.getenv("LOGFILE_NAME", "app.log")

# Create logs directory if it doesn't exist
log_dir = Path(LOGDIR)
log_dir.mkdir(exist_ok=True)
log_file_path = log_dir / LOGFILE_NAME

logger = logging.getLogger('app_logger')
# set the default log level
logger.setLevel(logging.INFO)

# create formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# create handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(log_file_path)

# set format to handlers
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add handlers to the logger
logger.handlers = [stream_handler, file_handler]
