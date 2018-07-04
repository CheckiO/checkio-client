from checkio_client.settings import conf
import urllib.request
import urllib.parse
import json

def api_request(path):
    domain_data = conf.default_domain_data
    req = urllib.request.Request(domain_data['url_main'] + path)
    req.add_header('CheckiOApiKey', domain_data['key'])
    res = urllib.request.urlopen(req) # TODO: all kind of errors
    return json.loads(res.read())

def get_mission_info(mission_slug):
    return api_request('/api/tasks/' + mission_slug + '/')


def get_user_missions():
    return api_request('/api/user-missions/')


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