import sys
import os
import configparser

__all__ = ['conf']
CUR_DIR = os.path.dirname(__file__)

VERSION = (0, 1, 3)

class Config(configparser.ConfigParser):
    foldername = os.path.join(os.path.expanduser("~"), '.checkio')
    filename = os.path.join(foldername, 'config.ini')

    domains = {
        'py': {
            'url_main': 'https://py.checkio.org',
            'server_port': 2325,
            'server_host': 'py-tester.checkio.org',
            'center_slug': 'python-3',
            'executable': sys.executable,
            'extension': 'py',
            'comment': '# '
        },
        'js': {
            'url_main': 'https://js.checkio.org',
            'server_port': 2345,
            'server_host': 'py-tester.checkio.org',
            'center_slug': 'js-node',
            #'executable': 'node',
            'extension': 'js',
            'comment': '// '
        }
    }

    inter_to_domain = {v['center_slug']: k for k,v in domains.items()}
    default_domain = 'py'

    repo_template = 'https://github.com/CheckiO/checkio-mission-template.git'

    local_uch_port = 2323

    uch_file = os.path.join(CUR_DIR, 'verification', 'uch.py')

    @property
    def default_domain_data(self):
        return self.domains[self.default_domain]

    @property
    def default_domain_section(self):
        return self[self.default_domain + '_checkio']
    
    

    def exists(self):
        return os.path.exists(self.filename)

    def save(self):
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)

        with open(self.filename, 'w') as f:
            self.write(f)

    def set_default_domain(self, domain):
        if domain not in self.domains:
            raise ValueError('Wrong Domain')
        setattr(self, 'default_domain', domain)

    def set_default_domain_by_inter(self, interpreter):
        self.set_default_domain(self.inter_to_domain[interpreter])

    def open(self):
        self.read(self.filename)
        for key in self['Main']:
            if hasattr(self, key):
                setattr(self, key, self['Main'][key])

        for d_key in self.domains:
            section_name = d_key + '_checkio'
            if not self.has_section(section_name):
                continue
            for key in self[section_name]:
                self.domains[d_key][key] = self[section_name][key]

conf = Config()
if conf.exists():
    conf.open()


