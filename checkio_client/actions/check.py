import sys
import subprocess
import time
import asyncio
from random import randint
import logging
import json
import os

from checkio_client.settings import conf
from checkio_client.api import get_mission_info, check_solution,\
    restore, run_solution
from checkio_client.utils.code import code_for_check, solutions_paths, parse_env_line
from checkio_client.actions.sync import sync_single_mission
from checkio_client.actions.init import main as main_init

SYSTEM_BLOCK_START = '---SYSTEMBLOCKSTART---'
SYSTEM_BLOCK_END = '---SYSTEMBLOCKEND---'


def lambda_game(func_name):
    def api_call(*args, **kwargs):
        return globals()[func_name + '_' + conf.default_domain_data['game']](*args, **kwargs)
    return api_call


def get_filename(args, print_filename=True):
    if hasattr(args, 'filename') and args.filename:
        filename = args.filename
        filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        return filename
    default_data = conf.default_domain_data
    if 'solutions' not in default_data:
        raise ValueError('Solutions folder is not defined')

    mission = args.mission[0].replace('_', '-')
    try:
        filename = solutions_paths()[mission]
    except KeyError:
        return None
    else:
        if print_filename:
            print('USING FILE: {}'.format(filename))
            print()
        return filename

def get_filename_init(args):
    filename = get_filename(args)
    if filename:
        return filename

        
    setattr(args, 'out', False)
    setattr(args, 'without_info', False)
    main_init(args)
    return get_filename(args)

main = lambda_game('main_check')

def main_check_cio(args):
    if '.' in args.mission[0]:
        filename = args.mission[0]
        with open(filename, encoding="utf-8") as fh:
            first_line = fh.readline().strip()
            cur_domain, mission = parse_env_line(first_line)
            if not cur_domain:
                raise ValueError('Invalid first line in the solution file')

            conf.set_default_domain(cur_domain)

    else:
        mission = args.mission[0].replace('_', '-')
        filename = get_filename(args, print_filename=False)

    domain_data = conf.default_domain_data

    if main_run(args):
        return

    print()
    print('Start checking...')
    print()
    mission_info = get_mission_info(mission)
    mission_id = mission_info['id']
    with open(filename, encoding="utf-8") as fh:
        data = check_solution(code_for_check(fh.read()), mission_id)

    new_version = False
    while data:
        block = data.pop(0)
        com = block[0]
        if com == 'start_in':
            print('*** ' + block[1] + ' ***' )
        elif com == 'in':
            if len(block) >= 4 and 'assert' in block[3]:
                new_version = True
                print('{} ...'.format(block[3]['assert']), end='')
            else:
                print('->' + str(block[1]))
        elif com == 'out':
            if len(block) >= 4 and 'correct' in block[3]:
                if block[3]['correct']:
                    print('ok')
                else:
                    print('Fail')
            else:
                print('<-' + str(block[1]))
        elif com == 'ext':
            res = block[1]
            if not res['result'] and not new_version:
                print('!!' + str(res['answer']))
        elif com == 'check':
            if block[1]:
                system_data = {
                    'info': 'passed',
                    'solutions_link': '{}/mission/{}/publications/'.format(
                            domain_data['url_main'], mission
                        ),
                    'add_link': '{}/mission/{}/publications/add/'.format(
                            domain_data['url_main'], mission
                        )
                }
                print()
                print('!!! Congratulation !!!')
                print()
                print('Link for checking solution of other users: ' + system_data['solutions_link'])
                print()
                print('Link for sharing solution: ' + system_data['add_link'])
                print()

                if args.sysinfo:
                    print(SYSTEM_BLOCK_START)
                    print(json.dumps(system_data, indent=1))
                    print(SYSTEM_BLOCK_END)

            else:
                print('!! Failed !!')
        elif com == 'wait':
            print('Waiting for the next piece of data...')
            time.sleep(block[2])
            print('Restore checking...')
            data = restore(block[1])
        else:
            print(block)

def main_check_eoc_local(args):
    from checkio_client.eoc.testing import execute_referee
    filename = get_filename(args)
    mission = args.mission[0].replace('_', '-')

    if args.recompile:
        from checkio_client.eoc.getters import recompile_mission
        recompile_mission(mission)
    logging.info('Using: ' + filename)
    execute_referee('check', mission, filename, ref_extra_volume=eoc_get_extra_volume(args))

async def eoc_websocket_check(args):
    import websockets

    mission = args.mission[0]
    filename = get_filename(args)
    if filename is None:
        filename = sync_single_mission(mission)
        if filename is None:
            print('Mission "{}" not found'.format(mission))
            return


    domain_data = conf.default_domain_data
    if 'key' not in domain_data:
        print('client is not configured. Please do $ checkio config')
        return

    logging.info('USING: %s', filename)

    with open(filename, encoding="utf-8") as fh:
        code = code_for_check(fh.read())

    async with websockets.connect(
            domain_data['ws_url'], extra_headers=websockets.http.Headers({
                'Cookie': 'apiKey=' + domain_data['key']
                })) as websocket:
        greeting = await websocket.recv()
        #print('greeting', greeting)

        await websocket.send(json.dumps({
            'action': 'check',
            'data': {
                'code': code,
                'env_name': domain_data['interpreter'],
                'mission': mission,
                'process': mission
            }}))

        while True:
            resp = await websocket.recv()
            resp = json.loads(resp)
            if resp['action'] == 'check':
                # stream = resp['data']['type'] == 'stdout' and sys.stdout or sys.stderr
                # print(resp['data']['result'], end='', file=stream, flush=True)
                c_data = resp['data']
                if c_data['type'] == 'pre_test':
                    print('\n - CALL', c_data['representation'])
                elif c_data['type'] == 'post_test':
                    if c_data['test_passed']:
                        print('\n - EXPECTED', c_data['expected_result'])
                    else:
                        print('\n - ACTUAL', c_data['actual_result'])
                        print('\n - EXPECTED', c_data['expected_result'])
                elif c_data['type'] == 'stdout':
                    print(c_data['result'], file=sys.stdout, flush=True, end='')
                elif c_data['type'] == 'stderr':
                    print(c_data['result'], file=sys.stderr, flush=True, end='')
                else:
                    print('UNKNOW', c_data)
            elif resp['action'] == 'checkDone':
                print('SUCCESS', resp['data']['success'])
                break


def main_check_eoc(args):
    if args.local:
        main_check_eoc_local(args)
    else:
        asyncio.get_event_loop().run_until_complete(eoc_websocket_check(args))

main_run = lambda_game('main_run')

def main_run_cio(args):
    if getattr(args, 'check', False):
        args.check = False # to avoid recursion
        return main(args)

    if '.' in args.mission[0]:
        filename = args.mission[0]
        with open(filename, encoding="utf-8") as fh:
            first_line = fh.readline().strip()
            cur_domain, mission = parse_env_line(first_line)
            if not cur_domain:
                raise ValueError('Invalid first line in the solution file')

            conf.set_default_domain(cur_domain)

    else:
        mission = args.mission[0].replace('_', '-')
        filename = get_filename_init(args)

    domain_data = conf.default_domain_data

    use_server_run = domain_data['use_server_run']

    if hasattr(args, 'check'):
        # it is running under the run function
        if use_server_run:
            if args.use_local_run:
                use_server_run = False
        else:
            if args.use_server_run:
                use_server_run = True

    if not use_server_run and not domain_data.get('executable'):
        raise ValueError('For the local run executable should be set')

    if not use_server_run:
        return subprocess.call((domain_data['executable'], filename))

    with open(filename, encoding="utf-8") as fh:
        data = run_solution(code_for_check(fh.read()))
    ret = False
    while data:
        block = data.pop(0)
        com = block[0]
        if com == 'err':
            print(block[1], end='')
            ret = True
        elif com == 'out':
            print(str(block[1]), end='')
        elif com == 'wait':
            data = restore(block[1])
        else:
            print(block)

    print()
    return ret

def eoc_get_extra_volume(args):
    if args.eoc_referee:
        return {
            args.eoc_referee: {
                'bind': '/src/checkio-referee/checkio_referee',
                'mode': 'rw'
            }
        }
    else:
        return {}

def main_run_eoc_local(args):
    from checkio_client.eoc.testing import execute_referee
    filename = get_filename(args)
    mission = args.mission[0].replace('_', '-')

    logging.info('Using: ' + filename)
    

    execute_referee('run', mission, filename, ref_extra_volume=eoc_get_extra_volume(args))

async def eoc_websocket_run(args):
    import websockets
    import json

    mission = args.mission[0]
    filename = get_filename(args)
    if filename is None:
        filename = sync_single_mission(mission)
        if filename is None:
            print('Mission "{}" not found'.format(mission))
            return

    domain_data = conf.default_domain_data
    if 'key' not in domain_data:
        print('client is not configured. Please do $ checkio config')
        return

    logging.info('USING:' + filename)

    with open(filename, encoding="utf-8") as fh:
        code = code_for_check(fh.read())

    async with websockets.connect(
            domain_data['ws_url'], extra_headers=websockets.http.Headers({
                'Cookie': 'apiKey=' + domain_data['key']
                })) as websocket:
        greeting = await websocket.recv()
        # print('greeting', greeting)

        await websocket.send(json.dumps({
            'action': 'run',
            'data': {
                'code': code,
                'env_name': domain_data['interpreter'],
                'mission': mission,
                'process': randint(10**5, 10**6)
            }}))

        while True:
            resp = await websocket.recv()
            resp = json.loads(resp)
            if resp['action'] == 'run':
                stream = resp['data']['type'] == 'stdout' and sys.stdout or sys.stderr
                print(resp['data']['result'], end='', file=stream, flush=True)
            elif resp['action'] == 'runDone':
                print('SUCCESS', resp['data']['success'])
                break


def main_run_eoc(args):
    if args.local:
        main_run_eoc_local(args)
    else:
        asyncio.get_event_loop().run_until_complete(eoc_websocket_run(args))

