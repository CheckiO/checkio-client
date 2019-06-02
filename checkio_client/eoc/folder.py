import os
import json


from checkio_client.eoc.settings import conf


def get_file_content(file_path):
    fh = open(file_path)
    try:
        return fh.read()
    finally:
        fh.close()


class Folder(object):
    def __init__(self, slug):
        assert slug, 'incorect slug parameter for Folder'
        self.u_slug = slug
        self.f_slug = slug.replace('-', '_')

    def exists(self):
        return os.path.exists(self.mission_folder())

    def image_name(self):
        return 'checkio/' + self.u_slug

    def image_name_cli(self):
        return 'checkio/cli__' + self.u_slug

    def mission_folder(self):
        return os.path.join(conf.missions_folder, self.f_slug)

    def mission_config_path(self):
        return os.path.join(self.mission_folder(), '.eoc.yaml')

    def compiled_folder_path(self):
        return os.path.join(conf.compiled_folder, self.f_slug)

    def container_compiled_folder_path(self):
        return os.path.join(conf.container_compiled_folder, self.f_slug)

    def verification_folder_path(self):
        return os.path.join(self.compiled_folder_path(), 'verification')

    def container_verification_folder_path(self):
        return os.path.join(self.container_compiled_folder_path(), 'verification')

    def referee_requirements(self):
        return os.path.join(self.verification_folder_path(), 'requirements.txt')

    def interface_cli_folder_path(self):
        return os.path.join(self.compiled_folder_path(), 'interfaces', 'checkio_cli')

    def interface_cli_main(self):
        return os.path.join(self.interface_cli_folder_path(), 'src', 'main.py')

    def interface_cli_requirements(self):
        return os.path.join(self.interface_cli_folder_path(), 'requirements.txt')

    def referee_folder_path(self):
        return os.path.join(self.verification_folder_path(), 'src')

    def envs_folder_path(self):
        return os.path.join(self.verification_folder_path(), 'envs')

    def compiled_referee_folder_path(self):
        return os.path.join(self.container_verification_folder_path(), 'src')

    def compiled_envs_folder_path(self):
        return os.path.join(self.container_verification_folder_path(), 'envs')

    def native_env_folder_path(self):
        return os.path.join(conf.native_folder, self.f_slug)

    def native_env_bin(self, call):
        return os.path.join(self.native_env_folder_path(), 'bin', call)

    def mission_config_read(self):
        return get_file_content(self.mission_config_path())

    def compiled_info_folder_path(self):
        return os.path.join(self.compiled_folder_path(), 'info')

    def compiled_info_file_content(self, file_name):
        try:
            return get_file_content(os.path.join(self.compiled_info_folder_path(), file_name))
        except IOError:
            return ''

    def mission_config_write(self, source_data):
        with open(self.mission_config_path(), 'w') as fh:
            json.dump({'source': source_data}, fh, sort_keys=True, indent=4)

    def mission_config(self):
        with open(self.mission_config_path()) as fh:
            return json.load(fh)

    def init_folder_path(self):
        return os.path.join(self.compiled_folder_path(), 'initial')

    def init_available_list(self):
        return os.listdir(self.init_folder_path())

    def init_file_path(self, interpreter):
        return os.path.join(self.init_folder_path(), interpreter)

    def initial_code(self, interpreter):
        return get_file_content(self.init_file_path(interpreter))

    def solution_path(self):
        extension = conf.default_domain_data['extension']
        return os.path.join(conf.solutions_folder, self.f_slug + '.' + extension)

    def solution_code(self):
        return get_file_content(self.solution_path())
