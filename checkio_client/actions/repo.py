from warnings import warn
import sys
import shutil
import os
import stat
import logging

from checkio_client.settings import conf

try:
    import git
except ImportError:
    print('''
if you want to work with repos please install GitPython
You can do it by doing:

{} -mpip install GitPython
'''.format(sys.executable))
    sys.exit()

def link_folder_to_repo(folder, repository):
    folder = os.path.abspath(folder)
    repo = git.Repo.init(folder)
    logging.info('Add files to repo')
    for root, dirs, files in os.walk(folder):
        if root.endswith('.git') or '/.git/' in root:
            continue

        # TODO: Skip pyc and __pycache__

        for file_name in files:
            abs_file_name = os.path.join(root, file_name)
            logging.info(abs_file_name)
            repo.index.add([abs_file_name])

    repo.index.commit("initial commit")
    origin = repo.create_remote('origin', repository)
    logging.info('Push to:' + repository)
    origin.push(repo.refs)
    origin.fetch()
    repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master)

def clone_repo_to_folder(template, folder):
    logging.info('Reciving template mission from ' + template + ' ...')
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
        logging.info('Send to git...')
        link_folder_to_repo(folder, args.repository)
    print('Done')

def main_link(args):
    folder = args.folder[0]
    repository = args.repository[0]
    link_folder_to_repo(folder, repository)
    print('Done')