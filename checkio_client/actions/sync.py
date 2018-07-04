import os

from checkio_client.api import get_user_missions
from checkio_client.utils.code import code_for_file, init_code_file
from checkio_client.settings import conf

def main(args):
    folder = args.folder
    with_unseen = args.include_unseen
    with_solved = not args.exclude_solved
    save_config = not args.without_config

    domain_data = conf.default_domain_data

    if not folder:
        folder = domain_data.get('solutions')
        if not folder:
            print('Select folder')
            return

    print('Rquesting...')
    data = get_user_missions()
    os.makedirs(folder, exist_ok=True)

    for item in data['objects']:
        if not item['isStarted'] and not with_unseen:
            continue

        if item['isSolved'] and not with_solved:
            continue

        mission = item['slug']
        code = item['code']
        description = item['description']

        filename = os.path.join(folder, mission.replace('-', '_') + '.' + domain_data['extension'])

        output = code_for_file(mission, code, 
            None if args.without_info else description)

        init_code_file(filename, output)

        print(filename + ' - Done')

        if save_config:
            conf.default_domain_section['solutions'] = os.path.abspath(folder)
            conf.save()


