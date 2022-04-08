import logging
import sys

def init_logger(file_name):
    log_format = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
    logging.basicConfig(filename=file_name, level=logging.DEBUG, format=log_format)
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)