import os
import logging
import asyncio
import json
from pprint import pprint

from checkio_client.eoc.getters import mission_git_getter, recompile_mission, rebuild_native,\
    rebuild_mission, can_check_mission
from checkio_client.eoc.initial import init_home_file

from checkio_client.eoc.folder import Folder
from checkio_client.settings import conf
from checkio_client.eoc.testing import execute_referee

def get_git(args):
    mission_git_getter(args.url, args.mission)
    recompile_mission(args.mission)
    if not args.without_container:
        rebuild_mission(args.mission)
    init_home_file(args.mission)

def reset_initial(args):
    init_home_file(args.mission, force=True)

def complile_mission(args):
    recompile_mission(args.mission)

def build_mission(args):
    rebuild_mission(args.mission)

def native_build_mission(args):
    rebuild_native(args.mission)

def init_mission(args):
    from checkio_client.actions.repo import link_folder_to_repo, clone_repo_to_folder
    domain_data = conf.default_domain_data
    mission = args.mission[0]
    folder = Folder(mission)

    
    if folder.exists():
        print('Folder exists already')
        return

    if args.template:
        template = args.template
    else:
        domain_data = conf.default_domain_data
        template = domain_data['repo_template']

    clone_repo_to_folder(template, folder.mission_folder())    

    if args.repository:
        print('Send to git...')
        link_folder_to_repo(folder.mission_folder(), args.repository)

    recompile_mission(mission)
    if not args.without_container:
        rebuild_mission(mission)
    init_home_file(mission)

    print('Done')

def send_battle_to_server(battle_json):
    import websockets

    domain_data = conf.default_domain_data
    async def send_to_websocket():
        async with websockets.connect(
            domain_data['ws_url'], extra_headers=websockets.http.Headers({
                'Cookie': 'apiKey=' + domain_data['key']
                })) as websocket:

            greeting = await websocket.recv()

            print('RESULT')
            try:
                data = json.loads(battle_json)
                pprint(data['result'])
            except json.decoder.JSONDecodeError as e:
                print('PARSE ERROR', '-'*10)
                print(e)
                print('-'*20)
                print(battle_json)
                print('-'*20)
            else:
                await websocket.send('{"action": "attack-save", "data": {"battle": ' + battle_json + ', "attacker": "a-test", "defender": "d-test"}}')

    asyncio.get_event_loop().run_until_complete(send_to_websocket())

def battle(args):
    from checkio_client.actions.check import get_filename
    filename = get_filename(args)
    mission = args.mission

    force_build = args.force_build

    if not force_build:
        force_build = not can_check_mission(mission)

    if force_build:
        mission_git_getter(args.repo, args.mission)
        recompile_mission(args.mission)
        rebuild_mission(args.mission)

    if args.recompile:
        recompile_mission(mission)
    logging.info('Using: ' + filename)

    ref_extra_volume = None
    if args.balance:
        logging.info('Balance from:' + args.balance)
        if not os.path.exists(args.balance):
            logging.info('Balance "' + args.balance + '" does not exists. Using was skiped')
        else:
            ref_extra_volume = {
                args.balance: {
                    'bind': '/opt/balance',
                    'mode': 'ro'
                }
            }

    battle_json = execute_referee('battle', mission, filename, ref_extra_volume=ref_extra_volume)

    if args.output_file:
        with open(args.output_file, 'w') as fh:
            fh.write(battle_json)
    else:
        send_battle_to_server(battle_json)
