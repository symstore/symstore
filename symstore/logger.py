import logging


def get_logger(name, log_file=None):
    l = logging.root
    l.name = name
    return l
