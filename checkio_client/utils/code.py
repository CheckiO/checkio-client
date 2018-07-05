import os
import stat

from checkio_client.settings import conf
from html.parser import HTMLParser

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
        code = description + '\n' + get_end_desc_line() + '\n\n' + code

    return '#!/usr/bin/env checkio --domain={domain} check {slug}\n\n{code}'.format(
            slug=slug,
            code=code.replace('\r', ''),
            domain=conf.default_domain
        )


def init_code_file(filename, code):
    with open(filename, 'w', encoding='utf-8') as fh: #TODO: if file exists
        fh.write(code)

    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)

def code_for_check(code):
    comment = conf.default_domain_data['comment']
    lines = code.split('\n')
    if lines[0].startswith('#!/usr/bin/env checkio'):
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

