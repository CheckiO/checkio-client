from warnings import warn
import sys
import shutil
import os

from checkio_client.settings import conf

try:
    import git
except ImportError:
    print('''
if you want to work with repos please install GitPython
You can do it by using pip3 install GitPython
'''.strip())
    sys.exit()

def link_folder_to_repo(folder, repository):
    folder = os.path.abspath(folder)
    repo = git.Repo.init(folder)
    print('Add files to repo')
    for root, dirs, files in os.walk(folder):
        if root.endswith('.git') or '/.git/' in root:
            continue

        # TODO: Skip pyc and __pycache__

        for file_name in files:
            abs_file_name = os.path.join(root, file_name)
            print(abs_file_name)
            repo.index.add([abs_file_name])

    repo.index.commit("initial commit")
    origin = repo.create_remote('origin', repository)
    print('Push to:' + repository)
    origin.push(repo.refs)
    origin.fetch()
    repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master)

def main_init(args):
    folder = args.folder[0]
    if os.path.exists(folder):
        print('Folder exists already')
        return
    print('Reciving template mission from ' + conf.repo_template + ' ...')
    git.Repo.clone_from(conf.repo_template, folder)
    shutil.rmtree(os.path.join(folder, '.git'))
    if args.repository:
        print('Send to git...')
        link_folder_to_repo(folder, args.repository)
    print('Done')

def main_link(args):
    folder = args.folder[0]
    repository = args.repository[0]
    link_folder_to_repo(folder, repository)
    print('Done')