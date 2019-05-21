import os

from checkio_client.settings import conf, TRANSFER_PARAMETERS

def main(args):
    if not conf.has_section('Main'):
        conf.add_section('Main')
    for domain_key in conf.domains:
        domain_section = domain_key + '_checkio'
        if not conf.has_section(domain_section):
            conf.add_section(domain_section)

    print('Config file {} will be created'.format(conf.filename))
    print('after short configuration process')

    print('Which domain you want to use by default? (first two letters are needed)')
    for dom, dom_conf in conf.domains.items():
        print('[{}] - {}'.format(dom, dom_conf['url_main']))
    print('by default:{}'.format(conf.default_domain))

    while True:
        new_domain = input('Code for domain[{}]:'.format(conf.default_domain)).strip()
        if not new_domain:
            new_domain = conf.default_domain
            break
        if new_domain not in conf.domains:
            continue
        break

    conf['Main']['default_domain'] = new_domain

    domain_data = conf.domains[new_domain]
    domain_section = new_domain + '_checkio'

    if domain_data['game'] != 'eoc':

        print('What is your KEY for {} ?'.format(domain_data['url_main']))
        print('You can find one on {}/profile/edit/'.format(domain_data['url_main']))
        while True:
            new_key = input('KEY:').strip()
            if not new_key:
                continue
            break

        conf[domain_section]['key'] = new_key

    for param in TRANSFER_PARAMETERS:
        if param in domain_data:
            conf[domain_section][param] = domain_data[param]

    default_solutions = domain_data['solutions']
    solutions_folder = input('Choose folder for your solutions [{}]'.format(default_solutions)).strip()
    if not solutions_folder:
        solutions_folder = default_solutions
    conf[domain_section]['solutions'] = solutions_folder


    if domain_data['game'] == 'eoc':
        default_source = domain_data['missions_source']
        source_folder = input('Choose folder for your source missions [{}]'.format(default_source)).strip()
        if not source_folder:
            source_folder = default_source

        conf[domain_section]['source'] = source_folder

    conf.save()

    print('Config file {} was updated.'.format(conf.filename))
    print('Thank you')
