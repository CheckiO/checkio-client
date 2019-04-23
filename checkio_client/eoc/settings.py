import os
from checkio_client.settings import conf as gen_conf

class Config:
    console_server_port = 7878
    def __getattr__(self, attr):
        return getattr(gen_conf, attr)

    @property
    def source_folder(self):
        return gen_conf.default_domain_data['source']
    
    @property
    def missions_folder(self):
        return os.path.join(self.source_folder, 'missions')

    @property
    def compiled_folder(self):
        return os.path.join(self.source_folder, 'compiled')

    @property
    def container_compiled_folder(self):
        return os.path.join(self.source_folder, 'container_compiled')

    @property
    def native_folder(self):
        return os.path.join(self.source_folder, 'native')

    @property
    def solutions_folder(self):
        return gen_conf.default_domain_data['solutions']




    

conf = Config()