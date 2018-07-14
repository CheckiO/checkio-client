from checkio_client.api import get_mission_info
from checkio_client.utils.code import code_for_file, init_code_file
from checkio_client.settings import conf

import os
import stat


def main(args):
    if args.out and args.filename:
        raise ValueError('out and filename can not be used together')

    mission = args.mission[0]
    filename = args.filename
    if not filename:
        filename = (
            mission.replace('-', '_') + '.' +
            conf.default_domain_data['extension']
        )


    if not args.out:
        print('Requesting...')

    data = get_mission_info(mission)
    code = data['code']
    description = data['description']

    output = code_for_file(mission, code, 
        None if args.without_info else description)

    if args.out:
        print(output)
        return


    init_code_file(filename, output)
    print('Done')