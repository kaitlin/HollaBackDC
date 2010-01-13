#### LOGGING #####
import logging
from django.conf import settings
# set up logging to file - see previous section for more details
FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
DATEFMT = '%y-%m-%d %H:%M'
if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG,
                    format='%(name)-12s: %(levelname)-8s %(message)s',
                    datefmt=DATEFMT)
else:
    logging.basicConfig(level=logging.WARNING,
                    format=FORMAT,
                    datefmt=DATEFMT)

