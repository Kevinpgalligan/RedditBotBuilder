import logging
import os.path
import os

LOGGER = logging.getLogger("root")

MAX_BYTES_PER_LOG = 5_000_000
NUM_LOG_FILES_TO_KEEP = 2
LOG_LEVEL = logging.INFO

def log_info(*args):
    log("info", *args)

def log_warning(*args):
    log("warning", *args)

def log_error(*args):
    log("error", *args)

def log(logger_fn_name, msg, *format_args):
    global LOGGER
    getattr(LOGGER, logger_fn_name)(msg, *format_args)

def configure(log_to_console, log_to_file, log_dir, bot_name):
    global LOGGER
    LOGGER = logging.getLogger(bot_name + "_logger")
    LOGGER.setLevel(LOG_LEVEL)
    if log_to_file:
        if not os.path.isdir(log_dir):
            raise ValueError("{} is not a directory, can't write logs there.".format(log_dir))
        if not os.access(log_dir, os.W_OK | os.X_OK):
            raise ValueError("Don't have write access to {}, can't write logs there.".format(log_dir))
        LOGGER.addHandler(
            RotatingFileHandler(
                # Use name of bot for uniqueness. It's assumed that the same bot
                # will not be running in another process, so shouldn't clash.
                os.path.join(log_dir, bot_name + ".log"),
                maxBytes=MAX_BYTES_PER_LOG,
                backupCount=NUM_LOG_FILES_TO_KEEP,
                encoding="utf-8"))
    if log_to_console:
        LOGGER.addHandler(logging.StreamHandler())
