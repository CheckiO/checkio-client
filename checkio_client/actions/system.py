from subprocess import Popen
import sys

def upgrade(args):
    line = '{} -mpip install --upgrade checkio_client'.format(sys.executable)
    print(line)
    Popen(line.split())
