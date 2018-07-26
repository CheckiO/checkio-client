from checkio_client.settings import conf

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
        new_domain = input('First two letters of the domain[{}]:'.format(conf.default_domain)).strip()
        if not new_domain:
            new_domain = conf.default_domain
            break
        if new_domain not in conf.domains:
            continue
        break

    conf['Main']['default_domain'] = new_domain

    domain_data = conf.domains[new_domain]

    print('What is your KEY for {} ?'.format(domain_data['url_main']))
    print('You can find one on {}/profile/edit/'.format(domain_data['url_main']))
    while True:
        new_key = input('KEY:').strip()
        if not new_key:
            continue
        break

    domain_section = new_domain + '_checkio'

    conf[domain_section]['key'] = new_key
    conf.save()

    print('Config file {} was updated.'.format(conf.filename))
    print('Thank you')
