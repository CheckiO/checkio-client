import tempfile
import shutil
import logging
import git
import os
import re
from docker.errors import BuildError, ImageNotFound

from distutils.dir_util import copy_tree

from checkio_client.eoc.folder import Folder
from checkio_client.eoc.testing import cleanup_containers
from checkio_docker.parser import MissionFilesCompiler
from checkio_docker.client import DockerClient

RE_REPO_BRANCH = re.compile('(.+?)\@([\w\-\_]+)$')

def logging_sys(command):
    logging.debug('Sys: %s', command)
    os.system(command)

def tmp_folder(folder):
    tmp = os.path.join(tempfile.mkdtemp(), 'mnt')
    shutil.copytree(folder, tmp)
    return tmp


def can_check_mission(slug):
    folder = Folder(slug)
    docker = DockerClient()

    try:
        docker.images.get(folder.image_name())
        docker.images.get(folder.image_name_cli())
    except ImageNotFound:
        return False
    else:
        return True


def mission_git_getter(url, slug):
    # TODO: checkout into mission solder
    # compile it
    # build docker
    # prepare cli interface
    folder = Folder(slug)
    destination_path = folder.mission_folder()

    logging.info('Getting a new mission through the git...')
    logging.info('from %s to %s', url, destination_path)

    if os.path.exists(destination_path):
        answer = input('Folder {} exists already.'
                           ' Do you want to overwite it? [y]/n :'.format(destination_path))
        if answer is '' or answer.lower().startswith('y'):

            if os.path.islink(destination_path):
                os.remove(destination_path)
            else:
                shutil.rmtree(destination_path)
        else:
            return


    if os.path.exists(url):
        logging.info('Linking folder %s -> %s', url, destination_path)
        os.symlink(os.path.abspath(url), destination_path)
        return

    re_ret = re.search(RE_REPO_BRANCH, url)
    if re_ret:
        checkout_url, branch = re_ret.groups()
    else:
        checkout_url = url
        branch = 'master'

    logging.debug('URL info: checkioout url:%s branch:%s', url, branch)

    try:
        git.Repo.clone_from(checkout_url, destination_path, branch=branch)
    except git.GitCommandError as e:
        raise Exception(u"{}, {}".format(e or '', e.stderr))
    folder.mission_config_write({
        'type': 'git',
        'url': url
    })
    logging.info('Prepare mission {} from {}'.format(slug, url))


def recompile_mission(slug):
    folder = Folder(slug)
    compiled_path = folder.compiled_folder_path()
    logging.info("Relink folder to %s", compiled_path)
    if os.path.exists(compiled_path):
        shutil.rmtree(compiled_path)

    mission_source = MissionFilesCompiler(compiled_path)
    mission_source.compile(source_path=folder.mission_folder(), use_link=True)


def rebuild_mission(slug):
    cleanup_containers()
    folder = Folder(slug)
    docker = DockerClient()
    verification_folder_path = folder.container_verification_folder_path()
    logging.info("[mission] Build docker image %s from %s", folder.image_name(), verification_folder_path)
    if os.path.exists(verification_folder_path):
        shutil.rmtree(verification_folder_path)

    copy_tree(folder.verification_folder_path(), verification_folder_path)

    try:
        docker.build(
            name_image=folder.image_name(),
            path=verification_folder_path)
    except BuildError as e:
        logging.warning('Build Error:')
        for item in e.build_log:
            logging.warning(item.get('stream'))
        logging.warning(list(e.build_log))
        logging.warning(e.msg)
        return
    rebuild_cli_interface(slug)


def rebuild_cli_interface(slug):
    folder = Folder(slug)
    build_folder = folder.interface_cli_folder_path()
    img_name = folder.image_name_cli()

    logging.info("[interface] Build docker image %s from %s", img_name, build_folder)

    docker = DockerClient()
    try:
        docker.build(
            name_image=img_name,
            path=tmp_folder(build_folder))
    except BuildError as e:
        logging.warning('Build Error:')
        for item in e.build_log:
            logging.warning(item.get('stream'))
        logging.warning(list(e.build_log))
        logging.warning(e.msg)



def rebuild_native(slug):
    folder = Folder(slug)
    logging.info('Building virtualenv in %s', folder.native_env_folder_path())
    if os.path.exists(folder.native_env_folder_path()):
        shutil.rmtree(folder.native_env_folder_path())

    logging_sys("virtualenv --system-site-packages -p python3 " + folder.native_env_folder_path())
    logging_sys("{pip3} install -r {requirements}".format(
        pip3=folder.native_env_bin('pip3'),
        requirements=folder.referee_requirements()
    ))
    logging_sys("{pip3} install -r {requirements}".format(
        pip3=folder.native_env_bin('pip3'),
        requirements=folder.interface_cli_requirements()
    ))