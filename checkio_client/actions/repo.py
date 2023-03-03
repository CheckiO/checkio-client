from warnings import warn
import sys
import shutil
import os
import stat
import logging
import subprocess

from checkio_client.settings import conf

try:
    import git
except ImportError:
    print(f'''
if you want to work with repos please install GitPython
You can do it by doing:

{sys.executable} -mpip install GitPython
''')
    sys.exit()

def link_folder_to_repo(repository: str) -> None:

    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', '"first commit"'], check=True)
    subprocess.run(['git', 'branch', '-M', 'master'], check=True)
    subprocess.run(['git', 'remote', 'add', 'origin', repository], check=True)
    subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)


def clone_repo_to_folder(template, folder):

    logging.info(f'Receiving template mission from {template}...')
    git.Repo.clone_from(template, folder)

    def remove_readonly(func, path, execinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(os.path.join(folder, '.git'), onerror=remove_readonly)


def main_init(args):

    folder = args.folder[0]
    domain_data = conf.default_domain_data
    if os.path.exists(folder):
        logging.info('Folder exists already')
        return

    if args.template:
        template = args.template
    else:
        domain_data = conf.default_domain_data
        template = domain_data['repo_template']

    clone_repo_to_folder(template, folder)
    

    if args.repository:
        # TODO: Skip pyc and __pycache__
        logging.info('Send to git...')
        try:
            os.chdir(folder)
            link_folder_to_repo(args.repository)
        finally:
            os.chdir('..')
    print('Done')

def main_link(args):

    folder = args.folder[0]
    try:
        if folder != ".":
            os.chdir(folder)
        link_folder_to_repo(args.repository[0])
    finally:
        if folder != ".":
            os.chdir('..')
        
    print('Done')
