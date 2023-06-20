import os
import time
import json
import asyncio
import logging
from pathlib import Path

from checkio_client.api import get_user_missions, save_code, get_user_single_mission,\
                                api_request, api_request_get, get_server_time
from checkio_client.utils.code import code_for_file, init_code_file, code_for_send,\
                            solutions_paths, gen_filename
from checkio_client.settings import conf


def sync_single_mission(mission):
    domain_data = conf.default_domain_data
    item = get_user_single_mission(mission)
    if item is None or item['stationName'] is None:
        return
    mission = item['slug']
    code = item['code']
    description = item['description']
    folder = domain_data.get('solutions')

    output = code_for_file(mission, code, description)

    filename = gen_filename(mission, item['stationName'], folder)
    init_code_file(filename, output)
    return filename


def save_sync_config(folder):
    domain_data = conf.default_domain_data
    inifile = Path(folder) / 'checkio.ini'
    if inifile.exists():
        return

    with open(str(inifile), 'w') as fh:
        fh.write('''
[Main]
domain = {domain}
            '''.format(domain=conf.default_domain))

    print('Folder config "{}" created'.format(inifile))


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

    if args.configure_only:
        conf.default_domain_section['solutions'] = os.path.abspath(folder)
        conf.save()
        return

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

    save_sync_config(folder)

async def send_strategy_file(websocket, name, content):
    logging.info('Send File: %s', name)
    server_time = get_server_time()
    await websocket.send(json.dumps({
        'action': 'save-strategy-file',
        'data': {
            'strategies': {
                name: {
                    'at': server_time,
                    'content': content
                }
            }
        }}))

def save_strategy_file(name, content):
    logging.info('Receive File: %s', name)
    domain_data = conf.default_domain_data
    folder = os.path.join(domain_data['solutions'], 'strategies')
    logging.info('Receive File: %s', os.path.join(folder, name))
    with open(os.path.join(folder, name), 'w') as fh:
        fh.write(content)

async def eoc_websocket_sync_strategy(remote_data, local_data):
    import websockets

    domain_data = conf.default_domain_data

    async with websockets.connect(
            domain_data['ws_url'], extra_headers=websockets.http.Headers({
                'Cookie': 'apiKey=' + domain_data['key']
                })) as websocket:
        greeting = await websocket.recv()

        for name, data in local_data.items():
            if name not in remote_data:
                await send_strategy_file(websocket, name, data['content'])
                continue

            r_data = remote_data.pop(name)

            if r_data['content'] == data['content']:
                continue

            if r_data['changed'] > data['changed']:
                await send_strategy_file(websocket, name, data['content'])
                continue

            save_strategy_file(name, r_data['content'])

        for name, r_data in remote_data.items():
            save_strategy_file(name, r_data['content'])

    print('DONE')


def eoc_strategies(args):
    domain_data = conf.default_domain_data
    
    remote_data = api_request('/api/console/private/')['strategies']
    server_time = get_server_time()

    for name in remote_data.keys():
        remote_data[name]['changed'] = server_time - remote_data[name]['at']

    folder = os.path.join(domain_data['solutions'], 'strategies')
    if not os.path.exists(folder):
        os.makedirs(folder)

    local_data = {}

    for filename in sorted(os.listdir(folder)):
            if not filename.endswith('.' + domain_data['extension']):
                continue
            abs_filename = os.path.join(folder, filename)

            if not os.path.isfile(abs_filename):
                continue


            

            f_stats = os.stat(abs_filename)
            t_changed = time.time() - f_stats.st_mtime

            with open(abs_filename) as fh:
                content = fh.read()

            local_data[filename] = {
                'changed': int(t_changed),
                'content': content,
            }

    asyncio.get_event_loop().run_until_complete(eoc_websocket_sync_strategy(remote_data, local_data))


async def eoc_websocket_rm_strategy(name):
    import websockets

    domain_data = conf.default_domain_data

    async with websockets.connect(
            domain_data['ws_url'], extra_headers=websockets.http.Headers({
                'Cookie': 'apiKey=' + domain_data['key']
                })) as websocket:
        greeting = await websocket.recv()

        logging.info('Remove Remote: %s', name)
        await websocket.send(json.dumps({
            'action': 'delete-strategy-file',
            'data': {
                'strategies': [name]
            }}))

    folder = os.path.join(domain_data['solutions'], 'strategies')
    filename = os.path.join(folder, name)
    if os.path.exists(filename):
        logging.info('Remove Local: %s', filename)
        os.remove(filename)


def eoc_rm_strategy(args):
    asyncio.get_event_loop().run_until_complete(eoc_websocket_rm_strategy(args.name))
