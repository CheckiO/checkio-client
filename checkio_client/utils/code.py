import os
import stat

from checkio_client.settings import conf
from html.parser import HTMLParser

START_ENV_LINE = '#!/usr/bin/env checkio'

def get_end_desc_line():
    comment = conf.default_domain_data['comment']
    return comment + 'END_DESC'

class DescriptionParser(HTMLParser):
    escaped = ''
    skip_stack = 0
    in_pre = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.skip_stack:
            self.skip_stack += 1
            return

        if 'for_info_only' in attrs.get('class', ''):
            self.skip_stack += 1
            return

        if tag == 'br':
            self.escaped += '\n'

        if tag == 'pre':
            self.in_pre = True

    def handle_endtag(self, tag):
        if self.skip_stack:
            self.skip_stack -= 1
            return

        if tag == 'p':
            self.escaped  += '\n\n'

        if tag == 'pre':
            self.in_pre = False

    def handle_data(self, data):
        if self.skip_stack:
            return

        if not self.in_pre:
            data = data.replace('\n', '').strip()

        self.escaped += data

def gen_filename(slug, station, folder=None):
    domain_data = conf.default_domain_data
    if folder is None:
        folder = domain_data.get('solutions')
    return os.path.join(folder, station, slug.replace('-', '_') + '.' + domain_data['extension'])

def gen_env_line(slug):
    return '#!/usr/bin/env checkio --domain={domain} run {slug}'.format(
            slug=slug,
            domain=conf.default_domain
        )


def escape_description(text):
    parser = DescriptionParser()
    parser.feed(text)
    return parser.escaped


def code_for_file(slug, code, html_description=None):
    code = code.strip()
    if html_description:
        description = escape_description(html_description)
        comment = conf.default_domain_data['comment']
        description = comment + ('\n' + comment).join(description.split('\n'))
        mission_link = (
            comment + conf.default_domain_data['url_main'] + 
            '/mission/' + slug + '/'
        )

        code = (
            mission_link + '\n\n' +
            description + '\n' +
            get_end_desc_line() + '\n\n' +
            code.strip()
        )

    return gen_env_line(slug) + '\n\n' + code.replace('\r', '')


def init_code_file(filename, code):
    folder = os.path.dirname(filename)
    os.makedirs(folder, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as fh: #TODO: if file exists
        fh.write(code)

    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


def code_for_check(code):
    comment = conf.default_domain_data['comment']
    lines = code.split('\n')
    if lines[0].startswith(START_ENV_LINE):
        lines[0] = ''

    end_line = get_end_desc_line()
    if end_line in lines:
        for i in range(len(lines)):
            last_line = lines[i] == end_line
            if lines[i].startswith(comment):
                lines[i] = ''
                
            if last_line:
                break

    return '\n'.join(lines)


def code_for_send(code):
    return code_for_check(code).replace('\r', '').strip()

def code_for_sync(code):
    delimiter = get_end_desc_line()
    if delimiter  in code:
        return code.split(delimiter + '\n')[-1]
    else:
        if code.startswith(START_ENV_LINE):
            return code[code.index('\n') + 1:]
        else:
            return code


def solutions_paths(folder=None, extension=None):
    domain_data = conf.default_domain_data
    if folder is None:
        folder = domain_data.get('solutions')

    if extension is None:
        extension = domain_data.get('extension')

    paths = {}
    if not os.path.exists(folder):
        return paths

    for (dirpath, dirnames, filenames) in os.walk(folder):
        for filename in filenames:
            if not filename.endswith('.' + extension):
                continue
            full_path = os.path.join(dirpath, filename)
            with open(full_path, 'r', encoding='utf-8') as fh:
                line = fh.readline()
                if not line.startswith('#!'):
                    continue
                mission_slug = line.split()[-1]
                if mission_slug in paths:
                    raise ValueError('Dublicate files {} and {}'.format(
                            full_path,
                            paths[mission_slug]
                        ))
                paths[mission_slug] = full_path
    return paths
