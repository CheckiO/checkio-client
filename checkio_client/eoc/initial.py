import os
import logging
import stat

from checkio_client.eoc.settings import conf
from checkio_client.eoc.folder import Folder
from checkio_client.utils.code import code_for_file


def init_home_file(slug):
    initial_file = conf.default_domain_data['interpreter']
    folder = Folder(slug)
    if not os.path.exists(folder.init_file_path(initial_file)):
        raise ValueError('Wrong initial file {}'.format(initial_file))
        # available_list = folder.init_available_list()
        # if not available_list:
        #     logging.warning('Do not support any language. Initials is empty.')
        #     return
        # default = available_list[0]
        # str_propose = '[{}]/{}'.format(default, '/'.join(available_list[1:]))
        # answer = input(('Mission "{}" doesn\'t support {}.' +
        #                     ' Please choose one out of available {}:').format(slug, interpreter,
        #                                                                       str_propose))
        # answer = answer.strip()
        # if not answer:
        #     answer = default

        # _, interpreter = set_mi(interpreter=answer, do_raise=False)
        # return init_home_file(slug, interpreter)

    write_solution(slug, initial_file, folder.solution_path())

def write_solution(slug, initial_file, solution_path):
    domain = conf.default_domain_data
    logging.info("Write a solution into %s for %s %s", solution_path, slug, initial_file)
    folder = Folder(slug)
    dirname = os.path.dirname(solution_path)
    os.makedirs(dirname, exist_ok=True)
    with open(solution_path, 'w', encoding='utf8') as fh:
        fh.write(
            code_for_file(slug, folder.initial_code(initial_file))
        )

    st = os.stat(solution_path)
    os.chmod(solution_path, st.st_mode | stat.S_IEXEC)