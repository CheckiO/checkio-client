from subprocess import Popen
import logging
import sys

from checkio_client.settings import conf
from .check import get_filename_init

def exec_command(args):
    logging.info('Open: %s', ' '.join(args))
    Popen(args)

def main(args):
    domain_data = conf.default_domain_data

    if 'editor' not in domain_data:
        logging.error('Please add editor to your checkio-client configuration')
        logging.error('Example: checkio config set editor /usr/local/bin/sublime')
        return

    if not args.mission:
        exec_command([domain_data['editor'], domain_data['solutions']])
        return

    setattr(args, 'mission', [args.mission.replace('_', '-')])
    filename = get_filename_init(args)
    exec_command([domain_data['editor'], filename])

def main_upgrade(args):
    exec_command([sys.executable, '-mpip', 'install', '--upgrade', 'checkio-client'])