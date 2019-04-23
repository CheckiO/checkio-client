import sys
import os
import logging
import socket
import time
import tempfile
from distutils.dir_util import copy_tree

from checkio_docker.client import DockerClient
from checkio_client.eoc.settings import conf
from checkio_client.eoc.folder import Folder
import docker

NAME_CLI_INTERFACE = 'checkio_cli_interface'
NAME_CLI_IMAGE = 'checkio_interface'
NAME_CLI_NETWORK = 'checkio_cli_bridge'

def wait_for_remove(func, list_kwargs=None):
    if list_kwargs is None:
        list_kwargs = {}

    client = docker.from_env()

    while True:
        for cont in client.containers.list(**list_kwargs):
            if func(cont):
                time.sleep(2)
                break
        else:
            return


def cleanup_containers():
    client = docker.from_env()

    for cont in client.containers.list(all=True):
        if cont.name.startswith('mission__'):
            cont.remove(force=True)

    try:
        container = client.containers.get(NAME_CLI_INTERFACE)
    except docker.errors.NotFound:
        return

    try:
        container.kill()
    except docker.errors.APIError:
        pass
    logging.info('Wait for removing {} ...'.format(NAME_CLI_INTERFACE))
    wait_for_remove(lambda a: a.name==NAME_CLI_INTERFACE)


def prepare_docker():
    client = docker.from_env()
    try:
        client.images.get(NAME_CLI_IMAGE)
    except docker.errors.ImageNotFound:
        build_path = os.path.join(os.path.dirname(__file__), NAME_CLI_IMAGE)
        logging.info('Build Docker Image {} from {}'.format(NAME_CLI_IMAGE, build_path))
        (_, logs) = client.images.build(
            path=build_path,
            tag=NAME_CLI_IMAGE + ':latest'
        )
        for line in logs:
            logging.info(line)

    try:
        client.networks.get(NAME_CLI_NETWORK)
    except docker.errors.NotFound:
        logging.info('Create Network {}'.format(NAME_CLI_NETWORK))
        client.networks.create(NAME_CLI_NETWORK, driver="bridge")

def start_docker(slug):
    command = "{} {} 1 2 {}".format(NAME_CLI_INTERFACE, conf.console_server_port, str(conf.log_level))
    client = DockerClient()
    folder = Folder(slug)

    logging.info('Verification: {}'.format(folder.verification_folder_path()))

    copy_tree(folder.verification_folder_path(), folder.container_verification_folder_path())
    for root, dirs, files in os.walk(folder.container_verification_folder_path()):
        for momo in dirs:
            os.chmod(os.path.join(root, momo), 0o777)
        for momo in files:
            os.chmod(os.path.join(root, momo), 0o777)

    

    return client.run(slug, command, 
        volumes={
            folder.compiled_referee_folder_path(): {
                    'bind': '/opt/mission/src',
                    'mode': 'rw'
                },
            folder.compiled_envs_folder_path(): {
                    'bind': '/opt/mission/envs',
                    'mode': 'rw'
                }
        },
        network_mode=NAME_CLI_NETWORK,
        name='mission__' + slug,
        detach=True)


def start_server(slug, interface_folder, action, path_to_code, python3,
                 tmp_file_name=None):
    env_name = conf.default_domain_data['interpreter']
    docker_filename = '/root/' + os.path.basename(path_to_code)
    client = docker.from_env()

    logging.info('Interface Folder {}'.format(interface_folder))
    return client.containers.run(NAME_CLI_IMAGE,
            ' '.join(('python', '/root/interface/src/main.py', slug, action, env_name, docker_filename,
                  str(conf.console_server_port), str(conf.log_level), tmp_file_name or '-')),
            volumes={
                interface_folder: {
                    'bind': '/root/interface',
                    'mode': 'rw'
                },
                path_to_code: {
                    'bind': docker_filename,
                    'mode': 'rw'
                }
            },
            ports={
                (str(conf.console_server_port) + '/tcp'): conf.console_server_port
            },
            name=NAME_CLI_INTERFACE,
            auto_remove=True,
            network_mode=NAME_CLI_NETWORK,
            stdout=True,
            detach=True,
            tty=True
        )


def execute_referee(command, slug, solution, without_container=False, interface_child=False,
                    referee_only=False, interface_only=False):
    def start_interface(tmp_file_name=None):
        return start_server(slug, folder.interface_cli_folder_path(), command, solution,
                            folder.native_env_bin('python3'), tmp_file_name)

    def start_container():
        return start_docker(slug)

    folder = Folder(slug)
    prepare_docker()
    if interface_only:
        return start_interface()

    cleanup_containers()

    cli_logs = start_interface()
    ref_logs = start_container()

    for line in cli_logs.logs(stream=True):
        try:
            print(line.decode('utf-8'), end="")
        except Exception as e:
            logging.error(e, exc_info=True)
            pass
