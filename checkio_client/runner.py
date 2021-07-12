from checkio_client.settings import conf

import argparse
from importlib import import_module
import sys
import shlex
from checkio_client.eoc_runner import init_subparsers as eoc_init_subparsers,\
    add_check_paramas
import logging
import platform

#import pdb; pdb.set_trace();

LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

parser = argparse.ArgumentParser(prog='checkio')
parser.add_argument('--domain', type=str)
parser.add_argument('-v', dest='verbose', default=3, type=int,
                    help='Scripts verbose level')
subparsers = parser.add_subparsers(help='subcommands')

p_config = subparsers.add_parser('config', help='configure the tool')
p_config.add_argument('--key', type=str)
p_config.set_defaults(module='config', config_not_required=True)

p_config_subparsers = p_config.add_subparsers(help='config subcommands')

p_config_show = p_config_subparsers.add_parser('show', help='show full config')
p_config_show.add_argument('--raw', action='store_true',
     help='show config.ini')
p_config_show.set_defaults(module='config', func='main_show')

p_config_set = p_config_subparsers.add_parser('set', help='set value for config')
p_config_set.add_argument('name', type=str)
p_config_set.add_argument('value', type=str)
p_config_set.set_defaults(module='config', func='main_set')

p_config_set = p_config_subparsers.add_parser('reset', help='reset name to default value (by removing key from config file)')
p_config_set.add_argument('name', type=str)
p_config_set.set_defaults(module='config', func='main_reset')

#sub_creation = parser.add_subparsers(title='Mission Creation')

p_repo_init = subparsers.add_parser('initrepo', help='creates a folder with an empty mission')
p_repo_init.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')
p_repo_init.add_argument('repository', type=str, nargs='?',
    metavar='repository',
    help='url to git repository')

p_repo_init.add_argument('--template', type=str,
    metavar='template',
    help='url to git repository you want to take as a template')

p_repo_init.set_defaults(module='repo', func='main_init')

p_repo_link = subparsers.add_parser('linkrepo', help='folder with mission link to a repository')
p_repo_link.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')

p_repo_link.add_argument('repository', type=str, nargs=1,
    metavar='repository',
    help='url to git repository of your mission')

p_repo_link.set_defaults(module='repo', func='main_link')

p_repo_convert_eoc = subparsers.add_parser('convertrepo-to-eoc', help='Conver CheckiO format missions to EoC format missions')
p_repo_convert_eoc.add_argument('cio', type=str,
    metavar='cio_folder',
    help='CheckiO Mission folder')

p_repo_convert_eoc.add_argument('eoc', type=str,
    metavar='eoc_folder',
    help='Empire of Code Mission folder')

p_repo_convert_eoc.add_argument('--git-push', type=str,
    metavar='git_push',
    help='url to git repository you want to push EoC repo after convertion')

p_repo_convert_eoc.set_defaults(module='repo_convert', func='to_eoc')


p_repo_check = subparsers.add_parser('checkrepo', help='you can test your mission folder on remote server')
p_repo_check.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')
p_repo_check.add_argument('--translation', type=str)
p_repo_check.set_defaults(module='repo_check')

p_check_after = subparsers.add_parser('check', help='test your solution')
p_check_after.add_argument('mission', type=str, nargs=1, metavar='mission',
    help='slug for mission you want to check')
p_check_after.add_argument('filename', type=str, nargs='?', metavar='filename',
    help='path to the file with solution')
p_check_after.add_argument('--sysinfo', action='store_true',
     help='add system info in the end')
add_check_paramas(p_check_after)
p_check_after.set_defaults(module='check')

p_autofill_repo = subparsers.add_parser('autofillrepo', help='fill up animation, referee, description and initial code by basic tests and passed names for function')
p_autofill_repo.add_argument('folder', type=str, default='.', nargs='?',
    metavar='folder',
    help='path to the repository folder')
p_autofill_repo.add_argument('--js-function', type=str)
p_autofill_repo.add_argument('--py-function', type=str)
p_autofill_repo.add_argument('--desc-tests', type=int, default=5)
p_autofill_repo.add_argument('--not-multy', action='store_true')
p_autofill_repo.set_defaults(module='autofill')

p_open = subparsers.add_parser('open', help='open editor for solving puzzles')
p_open.add_argument('mission', type=str, nargs='?', metavar='mission',
    help='slug for mission you want to open')
p_open.set_defaults(module='open')

p_upgrade = subparsers.add_parser('upgrade', help='upgrade current checkio-client')
p_upgrade.set_defaults(module='open', func='main_upgrade')

p_run_after = subparsers.add_parser('run', help='exec your solution')
p_run_after.add_argument('mission', type=str, nargs=1, metavar='mission',
    help='slug for mission you want to check')
p_run_after.add_argument('filename', type=str, nargs='?', metavar='filename',
    help='path to the file with solution')
p_run_after.add_argument('--check', action='store_true',
     help='and do check after')
p_run_after.add_argument('--sysinfo', action='store_true',
     help='add system info in the end')
add_check_paramas(p_run_after)
p_run_after.set_defaults(module='check', func='main_run')


p_init = subparsers.add_parser('init', help='create a file with solution')
p_init.add_argument('--without-info', action='store_true',
     help='do not include mission info')
p_init.add_argument('--out', action='store_true',
     help='stdout the source code')
p_init.add_argument('mission', type=str, nargs=1, metavar='mission',
    help='slug for mission')
p_init.add_argument('filename', type=str, nargs='?', metavar='filename',
    help='path to the file with solution')
p_init.set_defaults(module='init')

p_available = subparsers.add_parser('available', help='list of available missions')
p_available.set_defaults(module='available')

p_sync = subparsers.add_parser('sync', help='synchronize local solutions with server  (for now it just saves all files to a local folder)')
p_sync.add_argument('folder', type=str, nargs='?', metavar='folder',
    help='path to the folder for synchronization')
p_sync.add_argument('--without-info', action='store_true',
     help='do not include mission info')
p_sync.add_argument('--without-config', action='store_true',
     help='do not include mission into default solutions folder')
p_sync.add_argument('--exclude-unseen', action='store_true',
    help='exclude solutions for mission you haven\'t opened')
p_sync.add_argument('--exclude-solved', action='store_true',
    help='exclude solutions for mission you have solved already')
p_sync.add_argument('--configure-only', action='store_true',
    help='do not synchronize file, only change tool configuration')
p_sync.set_defaults(module='sync')

p_plugin = subparsers.add_parser('install-plugin', help='Install Web Plugin')
p_plugin.add_argument('--ff', action='store_true',
     help='install for FireFox')
p_plugin.add_argument('--chromium', action='store_true',
     help='install for Chromium')
p_plugin.add_argument('--chrome', action='store_true',
     help='install for Chrome')
p_plugin.set_defaults(module='plugin', func='install')

p_plugin = subparsers.add_parser('uninstall-plugin', help='Unstall Web Plugin')
p_plugin.add_argument('--ff', action='store_true',
     help='uninstall for FireFox')
p_plugin.add_argument('--chromium', action='store_true',
     help='uninstall for Chromium')
p_plugin.add_argument('--chrome', action='store_true',
     help='uninstall for Chrome')
p_plugin.set_defaults(module='plugin', func='uninstall')


eoc_init_subparsers(subparsers)

def apply_main_args(args=None):
    try:
        conf.set_default_domain(args.domain if args is not None and args.domain is not None else conf.default_domain)
    except ValueError as e:
        print(e)
        return True

    # if not 'key' in conf.default_domain_data and conf.exists():
    #     print('Key for domain ' + conf.default_domain + ' is not defined')
    #     return True

def main():
    # because of calling inside of #!/usr/bin/
    if platform.system() == 'Windows':
        call_args = sys.argv[1:]
    else:
        call_args = sum(map(lambda a: shlex.split(a), sys.argv[1:]), [])
    args = parser.parse_args(call_args)

    logging.basicConfig(level=LEVELS[args.verbose])

    # because I don't knoe how to get log_level from logging
    logging.log_level = LEVELS[args.verbose]

    try:
        module = import_module('checkio_client.actions.' + args.module)
    except AttributeError:
        if not conf.exists():
            print('In order to start using CheckiO client')
            print('It should be configured first:')
            print()
            print('   $ checkio config')
            print()

        parser.print_help()
    else:
        if not getattr(args, 'config_not_required', False) and apply_main_args(args):
            return
        if hasattr(args, 'func'):
            func_name = args.func
        else:
            func_name = 'main'
        getattr(module, func_name)(args)