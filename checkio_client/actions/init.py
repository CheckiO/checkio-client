from checkio_client.api import get_mission_info
from checkio_client.utils.code import code_for_file, init_code_file

import os
import stat


def main(args):
    mission = args.mission[0]
    filename = args.filename

    if filename:
        print('Requesting...')

    data = get_mission_info(mission)
    code = data['code']
    description = data['description']

    output = code_for_file(mission, code, 
        None if args.without_info else description)

    if not filename:
        print(output)
        return


    init_code_file(filename, output)
    print('Done')