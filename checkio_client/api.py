from checkio_client.settings import conf, VERSION
import urllib.request
import urllib.parse
import requests
from urllib.error import HTTPError
import json
import logging

from checkio_client.settings import conf


STR_VERSION = '.'.join(map(str, VERSION))


def lambda_game(func_name):
    def api_call(*args, **kwargs):
        return globals()[func_name + '_' + conf.default_domain_data['game']](*args, **kwargs)
    return api_call

api_request = lambda_game('api_request')    

def api_request_cio(path, data=None):
    domain_data = conf.default_domain_data

    logging.debug('REQ: ' + domain_data['url_main'] + path)
    logging.debug('DATA: ' + str(data))

    if data and isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(domain_data['url_main'] + path, data=data)
    req.add_header('CheckiOApiKey', domain_data['key'])
    req.add_header('X-CheckiO-Client-Version', STR_VERSION)
    try:
        res = urllib.request.urlopen(req) # TODO: all kind of errors
    except HTTPError as e:
        resp = json.loads(e.read().decode('utf-8'))
        if resp.get('error') == 'OldClient':
            raise ValueError('Please update CheckiO console tool. checkio upgrade')
        else:
            raise
    resp_text = res.read().decode('utf-8')
    logging.debug('RESP: ' + resp_text)
    return json.loads(resp_text)

def api_request_eoc(path, data=None):
    domain_data = conf.default_domain_data

    if data is None:
        data = {}

    data.update({
        'api_key': domain_data['key']
    })
    logging.debug('REQ: ' + domain_data['url_main'] + path)
    logging.debug('DATA: ' + str(data))

    request_data = json.dumps(data)

    response = requests.post(
        domain_data['url_main'] + path,
        request_data, headers={'content-type': 'application/json'})

    logging.debug('RESP: ' + response.text)
    return json.loads(response.text)

def api_request_get(path):
    domain_data = conf.default_domain_data
    logging.debug('REQ GET: ' + domain_data['url_main'] + path)

    response = requests.get(
        domain_data['url_main'] + path, headers={'content-type': 'application/json'})

    logging.debug('RESP: ' + response.text)
    return json.loads(response.text)

def get_server_time():
    return int(api_request_get('/api/time/')['time'])

def get_mission_info(mission_slug):
    return api_request('/api/tasks/' + mission_slug + '/')

def info_eoc_to_cio(m):
    return {
        'stationName': m['type'],
        'description': m['description'],
        'isStarted': False,
        'isSolved': False,
        'slug': m['slug'],
        'secondsPast': m.get('seconds_past', 0),
        'code': m['user_solution'] or m['initial_code'],
        'id': m['slug']
    }

get_user_missions = lambda_game('get_user_missions')

def get_user_missions_cio():
    return api_request('/api/user-missions/')

def get_user_missions_eoc():
    data = api_request('/api/console/list-missions/')
    return {
        'objects': map(info_eoc_to_cio, data)
    }


get_user_single_mission = lambda_game('get_user_single_mission')

def get_user_single_mission_cio(mission):
    pass

def get_user_single_mission_eoc(mission):
    data = api_request('/api/console/list-missions/', {'mission_slug': mission})
    if not data:
        return
    return info_eoc_to_cio(data[0])




save_code = lambda_game('save_code')

def save_code_cio(code, task_id):
    domain_data = conf.default_domain_data
    return api_request('/mission/js-task-save/', {
        'code': code,
        'task_num': task_id,
        'runner': domain_data['center_slug']
    })

def save_code_eoc(code, mission_slug):
    return api_request('/api/console/save-solution/', {
        'code': code,
        'mission_slug': mission_slug
    })

def center_request(path, data):
    domain_data = conf.default_domain_data

    req_data = {'apikey': domain_data['key']}
    req_data.update(data)
    http_data = urllib.parse.urlencode(req_data).encode()
    full_path = domain_data['url_main'] + '/center/1' + path
    req = urllib.request.Request(full_path, data=http_data)

    res = urllib.request.urlopen(req) # TODO: all kind of errors
    return json.loads('[' + res.read().decode('utf-8')[:-1] + ']')

def check_solution(code, task_id):
    domain_data = conf.default_domain_data
    return center_request('/ucheck/', {
            'code': code,
            'task_num': str(task_id),
            'runner': domain_data['center_slug']
        })

def run_solution(code):
    domain_data = conf.default_domain_data
    return center_request('/run/', {
            'code': code,
            'runner': domain_data['center_slug']
        })


def restore(connection_id):
    return center_request('/restore/', {
            'connection_id': connection_id,
        })