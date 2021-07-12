import sys
import os
import configparser
from copy import deepcopy
import platform
import socket

__all__ = ['conf']
CUR_DIR = os.path.dirname(__file__)

VERSION = (0, 2, 15)

TRANSFER_PARAMETERS = ('executable', 'editor', 'solutions');

CIO_TEMPLATE_FOLDER = 'https://github.com/CheckiO/checkio-mission-template.git'
EOC_TEMPLATE_FOLDER = 'https://github.com/oduvan/eoc-template.git'

def get_fodler(folder):
    return os.path.expanduser(os.path.join('~', folder))

class Config(configparser.ConfigParser):
    xdg = os.getenv('XDG_CONFIG_HOME')
    if xdg:
        foldername = os.path.join(xdg, 'checkio')
    else:
        foldername = os.path.join(os.path.expanduser("~"), '.checkio')
    filename = os.path.join(foldername, 'config.ini')
    editor = 'open'
    docker_ip = '172.17.0.1'
    log_level = 20
    tmp_folder = None
    if platform.system() == 'Linux':
        editor = 'xdg-open'
    elif platform.system() == 'Windows':
        editor = 'C:\\Program Files\\Sublime Text 3\\subl.exe'

    domains = {
        'py': {
            'url_main': 'https://py.checkio.org',
            'server_port': 2325,
            'server_host': 'py-tester.checkio.org',
            'center_slug': 'python-3',
            'executable': sys.executable,
            'extension': 'py',
            'comment': '# ',
            'game': 'cio',
            'editor': editor,
            'solutions': get_fodler('py_checkio_solutions'),
            'repo_template': CIO_TEMPLATE_FOLDER,
        },
        'js': {
            'url_main': 'https://js.checkio.org',
            'server_port': 2345,
            'server_host': 'js-tester.checkio.org',
            'center_slug': 'js-node',
            #'executable': 'node',
            'extension': 'js',
            'comment': '// ',
            'game': 'cio',
            'editor': editor,
            'solutions': get_fodler('js_checkio_solutions'),
            'repo_template': CIO_TEMPLATE_FOLDER,
        },
        'epy': {
            'url_main': 'https://empireofcode.com',
            'ws_url': 'wss://empireofcode.com/ws/',
            'server_port': 2325,
            'server_host': 'api.empireofcode.com',
            'center_slug': 'eoc-python',
            'executable': sys.executable,
            'extension': 'py',
            'comment': '# ',
            'game': 'eoc',
            'editor': editor,
            'solutions': get_fodler('py_eoc_solutions'),
            'missions_source': get_fodler('py_eoc_source'),
            'interpreter': 'python_3',
            'repo_template': EOC_TEMPLATE_FOLDER,
        },
        'ejs': {
            'url_main': 'https://empireofcode.com',
            'ws_url': 'wss://empireofcode.com/ws/',
            'server_port': 2345,
            'server_host': 'api.empireofcode.com',
            'center_slug': 'eoc-js-node',
            'extension': 'ts',
            'comment': '// ',
            'game': 'eoc',
            'editor': editor,
            'solutions': get_fodler('js_eoc_solutions'),
            'missions_source': get_fodler('js_eoc_source'),
            'interpreter': 'js_node',
            'repo_template': EOC_TEMPLATE_FOLDER,
        }
    }

    _initial_domains = deepcopy(domains)

    inter_to_domain = {v['center_slug']: k for k,v in domains.items()}
    default_domain = 'py'

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

    def reload(self):
        self.domains = deepcopy(self._initial_domains)
        self.open()

conf = Config()
if conf.exists():
    conf.open()


