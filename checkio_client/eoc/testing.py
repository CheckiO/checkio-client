import sys
import os
import logging
import socket
import time
import tempfile
import shutil
from datetime import datetime
from distutils.dir_util import copy_tree

from checkio_docker.client import DockerClient
from checkio_client.eoc.settings import conf
from checkio_client.eoc.folder import Folder
import docker

NAME_CLI_INTERFACE = 'checkio_cli_interface'
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


def tmp_folder(folder):
    tmp = os.path.join(tempfile.mkdtemp(), 'mnt')
    shutil.copytree(folder, tmp)
    return tmp


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
    logging.info('Wait for killing {} ...'.format(NAME_CLI_INTERFACE))
    wait_for_remove(lambda a: a.name==NAME_CLI_INTERFACE)

    try:
        container.remove()
    except docker.errors.APIError:
        pass

    logging.info('Wait for removing {} ...'.format(NAME_CLI_INTERFACE))
    wait_for_remove(lambda a: a.name==NAME_CLI_INTERFACE, {
            'all': True
        })



def prepare_docker():
    client = docker.from_env()

    try:
        client.networks.get(NAME_CLI_NETWORK)
    except docker.errors.NotFound:
        logging.info('Create Network {}'.format(NAME_CLI_NETWORK))
        client.networks.create(NAME_CLI_NETWORK, driver="bridge")

def start_docker(slug, ref_extra_volume=None):
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

    volumes={
            tmp_folder(folder.compiled_referee_folder_path()): {
                    'bind': '/opt/mission/src',
                    'mode': 'rw'
                },
            tmp_folder(folder.compiled_envs_folder_path()): {
                    'bind': '/opt/mission/envs',
                    'mode': 'rw'
                }
        }

    if ref_extra_volume is not None:
        volumes.update(ref_extra_volume)

    return client.run(slug, command, 
        volumes=volumes,
        network_mode=NAME_CLI_NETWORK,
        name='mission__' + slug,
        detach=True,
        ports={'4444/tcp': 4444})


def start_server(slug, interface_folder, action, path_to_code, python3,
                 tmp_file_name=None, ref_extra_volume=None):
    domain_data = conf.default_domain_data
    env_name = domain_data['interpreter']

    docker_filename = '/root/' + os.path.basename(path_to_code)
    client = docker.from_env()
    folder = Folder(slug)

    logging.info('Interface Folder {}'.format(interface_folder))
    volumes={
                tmp_folder(interface_folder): {
                    'bind': '/root/interface',
                    'mode': 'rw'
                },
                path_to_code: {
                    'bind': docker_filename,
                    'mode': 'rw'
                }
            }

    if ref_extra_volume is not None:
        volumes.update(ref_extra_volume)

    if conf.tmp_folder:
        volumes[conf.tmp_folder] = {
            'bind': '/root/tmp',
            'mode': 'rw'
        }
    
    if 'solutions' in domain_data:
        volumes[domain_data['solutions']] = {
            'bind': '/root/solutions',
            'mode': 'rw'
        }

    return client.containers.run(folder.image_name_cli(),
            ' '.join(('python -u', '/root/interface/src/main.py', slug, action, env_name, docker_filename,
                  str(conf.console_server_port), str(conf.log_level), tmp_file_name or '-')),
            volumes=volumes,
            ports={
                (str(conf.console_server_port) + '/tcp'): conf.console_server_port
            },
            name=NAME_CLI_INTERFACE,
            network_mode=NAME_CLI_NETWORK,
            stdout=True,
            detach=True,
            tty=True
        )


def execute_referee(command, slug, solution, without_container=False, interface_child=False,
                    referee_only=False, interface_only=False, ref_extra_volume=None):
    def start_interface(tmp_file_name=None):
        return start_server(slug, folder.interface_cli_folder_path(), command, solution,
                            folder.native_env_bin('python3'), tmp_file_name, ref_extra_volume)

    def start_container():
        return start_docker(slug, ref_extra_volume)

    client = docker.from_env()
    folder = Folder(slug)

    prepare_docker()
    if interface_only:
        return start_interface()

    cleanup_containers()

    cli_logs = start_interface()
    ref_logs = start_container()
    cli_read_size = 0
    ref_read_size = 0
    system_data = ''
    is_system_collecting = False
    SYSTEM_START = '---SYSTEM---'
    SYSTEM_END = '---END-SYSTEM---'

    while True:
        #print('...', client.containers.get(cli_logs.id).status)

        cli_data = cli_logs.logs()[cli_read_size:]
        cli_read_size += len(cli_data)

        ref_data = ref_logs.logs()[ref_read_size:]
        ref_read_size += len(ref_data)

        if cli_data:
            cli_data = cli_data.decode('utf-8')
            was_splited = False

            if not is_system_collecting and SYSTEM_START in cli_data:
                cli_data, new_system_data = cli_data.split(SYSTEM_START)

                if SYSTEM_END in new_system_data:
                    new_system_data, end_cli_data = new_system_data.split(SYSTEM_END)
                    cli_data += end_cli_data
                    is_system_collecting = False
                else:
                    is_system_collecting = True


                system_data += new_system_data
                was_splited = True


            if is_system_collecting and SYSTEM_END in cli_data:
                new_system_data, cli_data = cli_data.split(SYSTEM_END)
                system_data += new_system_data
                is_system_collecting = False
                was_splited = True

            if is_system_collecting and not was_splited:
                system_data += cli_data
                cli_data = ''

            

            #print ('-'* 5 , 'CLI')
            print(cli_data)
            #print('-'*5, 'SYS')


        if ref_data:
            print(ref_data.decode('utf-8'))

        if (client.containers.get(cli_logs.id).status, 
             client.containers.get(ref_logs.id).status) == ('exited', 'exited'):
            break

        time.sleep(0.01)

    return system_data

        

    # for line in cli_logs.logs(stream=True):
    #     try:
    #         print(line.decode('utf-8'), end="")
    #     except Exception as e:
    #         logging.error(e, exc_info=True)
    #         pass
