from subprocess import Popen
import sys
import logging

def upgrade(args):
    line = '{} -mpip install --upgrade checkio_client'.format(sys.executable)
    logging.debug(line)
    Popen(line.split())
