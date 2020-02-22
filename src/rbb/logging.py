import logging
import os.path
import os


MAX_BYTES_PER_LOG = 5_000_000
NUM_LOG_FILES_TO_KEEP = 2
LOG_LEVEL = logging.INFO

LOGGER = logging.getLogger("null-logger")
LOGGER.addHandler(logging.NullHandler())

def log_info(*args):
    global LOGGER
    LOGGER.info(*args)

def log_warning(*args):
    global LOGGER
    LOGGER.warning(*args)

def log_error(*args):
    global LOGGER
    LOGGER.error(*args)

def configure(log_to_console, log_to_file, log_dir, bot_name):
    global LOGGER
    LOGGER = logging.getLogger(bot_name + "_logger")
    LOGGER.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        LOGGER.addHandler(console_handler)
    if log_to_file:
        if not os.path.isdir(log_dir):
            raise ValueError("{} is not a directory, can't write logs there.".format(log_dir))
        if not os.access(log_dir, os.W_OK | os.X_OK):
            raise ValueError("Don't have write access to {}, can't write logs there.".format(log_dir))
        # Use name of bot for uniqueness. It's assumed that the same bot
        # will not be running in another process, so shouldn't clash.
        log_path = os.path.abspath(os.path.join(log_dir, bot_name + ".log"))
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_BYTES_PER_LOG,
            backupCount=NUM_LOG_FILES_TO_KEEP,
            encoding="utf-8")
        file_handler.setFormatter(formatter)
        LOGGER.addHandler(file_handler)
        LOGGER.info("Logging to file %s", log_path)
