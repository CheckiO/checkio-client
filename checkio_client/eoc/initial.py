import os
import logging
import stat

from checkio_client.eoc.settings import conf
from checkio_client.eoc.folder import Folder
from checkio_client.utils.code import code_for_file


def init_home_file(slug, force=False):
    initial_file = conf.default_domain_data['interpreter']
    folder = Folder(slug)

    solution = folder.solution_path()
    if os.path.exists(solution) and not force:
        return

    write_solution(slug, initial_file, solution)

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