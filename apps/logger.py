"""
Import debug function from here to output debugging information.
Set LOG_FILE in settings to customize output file.
"""
import logging

from django.conf import settings

def getlogger():
    logger = logging.getLogger()
    hdlr = logging.FileHandler(getattr(settings, 'LOG_FILE', 'byteflow.log'))
    formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s','%Y-%m-%d %a %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)

    return logger

def debug(*msgs):
    logger = getlogger()
    logger.debug(', '.join(map(str, msgs)))
