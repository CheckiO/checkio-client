import os
import time

from checkio_client.api import get_user_missions, save_code
from checkio_client.utils.code import code_for_file, init_code_file, code_for_send,\
                            solutions_paths, gen_filename
from checkio_client.settings import conf

def main(args):
    folder = args.folder
    with_unseen = not args.exclude_unseen
    with_solved = not args.exclude_solved
    save_config = not args.without_config

    domain_data = conf.default_domain_data

    if not folder:
        folder = domain_data.get('solutions')
        if not folder:
            print('Select folder')
            return
        print('Using folder "{}"'.format(folder))

    paths = solutions_paths(folder)

    print('Requesting...')
    data = get_user_missions()
    for item in data['objects']:
        if not item['isStarted'] and not with_unseen:
            continue

        if item['isSolved'] and not with_solved:
            continue

        mission = item['slug']
        code = item['code']
        description = item['description']

        output = code_for_file(mission, code, 
            None if args.without_info else description)

        # file exist
        if mission not in paths:
            filename = gen_filename(mission, item['stationName'], folder)
            init_code_file(filename, output)
            print(filename + ' - Created')
            continue

        filename = paths[mission]
        f_stats = os.stat(filename)
            

        # file changed
        with open(filename, 'r', encoding='utf-8') as fh:
            local_code = fh.read()
            if code_for_send(local_code) == code_for_send(output):
                continue
        
        t_changed = time.time() - f_stats.st_mtime

        # local file have been changed
        if not item['secondsPast'] or t_changed < item['secondsPast']:
            print(filename + ' - Sending... ', end='')
            save_code(code_for_send(local_code), item['id'])
            print('Done')

        # file was changed through the web interface
        else:
            init_code_file(filename, output)
            print(filename + ' - Overwritten')


    if save_config:
        conf.default_domain_section['solutions'] = os.path.abspath(folder)
        conf.save()


