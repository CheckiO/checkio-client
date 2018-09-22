from checkio_client.settings import conf

import argparse
from importlib import import_module

parser = argparse.ArgumentParser(prog='checkio')
parser.add_argument('--domain', type=str, default=conf.default_domain)
subparsers = parser.add_subparsers(help='subcommands')

p_config = subparsers.add_parser('config', help='configure the tool')
p_config.add_argument('--key', type=str)
p_config.set_defaults(module='config', config_not_required=True)

#sub_creation = parser.add_subparsers(title='Mission Creation')

p_repo_init = subparsers.add_parser('initrepo', help='creates a folder with an empty mission')
p_repo_init.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')
p_repo_init.add_argument('repository', type=str, nargs='?',
    metavar='repository',
    help='url to git repository')

p_repo_init.set_defaults(module='repo', func='main_init')

p_repo_link = subparsers.add_parser('linkrepo', help='folder with mission link to a repository')
p_repo_link.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')

p_repo_link.add_argument('repository', type=str, nargs=1,
    metavar='repository',
    help='url to git repository')

p_repo_link.set_defaults(module='repo', func='main_link')


p_repo_check = subparsers.add_parser('checkrepo', help='you can test your mission folder on remote server')
p_repo_check.add_argument('folder', type=str, default='.', nargs=1,
    metavar='folder',
    help='path to the repository folder')
p_repo_check.set_defaults(module='repo_check')

p_check_after = subparsers.add_parser('check', help='test your solution')
p_check_after.add_argument('mission', type=str, nargs=1, metavar='mission',
    help='slug for mission you want to check')
p_check_after.add_argument('filename', type=str, nargs='?', metavar='filename',
    help='path to the file with solution')
p_check_after.set_defaults(module='check')


p_run_after = subparsers.add_parser('run', help='exec your solution')
p_run_after.add_argument('mission', type=str, nargs=1, metavar='mission',
    help='slug for mission you want to check')
p_run_after.add_argument('filename', type=str, nargs='?', metavar='filename',
    help='path to the file with solution')
p_run_after.add_argument('--check', action='store_true',
     help='and do check after')
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
p_sync.set_defaults(module='sync')

p_plugin = subparsers.add_parser('install-plugin', help='configure the tool')
p_plugin.set_defaults(module='plugin', func='install')

p_plugin = subparsers.add_parser('uninstall-plugin', help='configure the tool')
p_plugin.set_defaults(module='plugin', func='uninstall')

def apply_main_args(args=None):
    try:
        conf.set_default_domain(args.domain if args is not None else conf.default_domain)
    except ValueError as e:
        print(e)
        return True

    if not 'key' in conf.default_domain_data and conf.exists():
        print('Key for domain ' + conf.default_domain + ' is not defined')
        return True

def main():
    args = parser.parse_args()
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