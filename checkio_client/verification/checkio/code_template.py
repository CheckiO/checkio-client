import json

try:
    import django
except ImportError:
    import sys
    raise ImportError('In order to use io_template you should install Django first. Please do {} -mpip install django'.format(sys.executable))

from django import template
from django.conf import settings
from django.template import Template, Context, NodeList
from django.template.loader_tags import BlockNode


settings.configure(TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates',}])
django.setup()

register = template.Library()


class JEncoder(json.JSONEncoder):
    def iterencode(self, value, *args, **kwargs):
        if isinstance(value, set):
            return 'new Set(' + json.dumps(list(value), cls=JEncoder) + ')'

        from decimal import Decimal
        if isinstance(value, Decimal):
            return str(value)

        from datetime import datetime, date
        if isinstance(value, date):
            return 'new Date({}, {}, {})'.format(
                value.year,
                value.month - 1,
                value.day,
            )
        if isinstance(value, datetime):
            return 'new Date({}, {}, {}, {}, {}, {})'.format(
                value.year,
                value.month - 1,
                value.day,
                value.hour,
                value.minute,
                value.second,
            )
        return super().iterencode(value, *args, **kwargs)


@register.filter(name='j')
def filter_json_dumps(val):
    return json.dumps(val, cls=JEncoder)


@register.filter(name='j_args')
def filter_json_dumps_args(vals):
    return ", ".join([json.dumps(val, cls=JEncoder) for val in vals])


@register.filter(name='p')
def filter_repr(val):
    return repr(val)


@register.filter(name='p_args')
def filter_repr_args(vals):
    return ", ".join([repr(val) for val in vals])


class StripBlockNode(BlockNode):
    def __init__(self, block_node):
        super().__init__(block_node.name, block_node.nodelist, block_node.parent)

    def render(self, *args, **kwargs):
        return super().render(*args, **kwargs).strip()

class CodeTemplate(Template):
    def __init__(self, *args, one_node=None, filter_nodes=None, **kwargs):
        self.one_node = one_node
        self.filter_nodes = filter_nodes
        super().__init__(*args, **kwargs)

    def replace_nodes(self, nodes):
        for i, node in enumerate(nodes):
            if isinstance(node, BlockNode):
                nodes[i] = StripBlockNode(node)
            
            if hasattr(node, 'nodelist'):
                self.replace_nodes(node.nodelist)
            elif hasattr(node, 'nodelist_loop'):
                self.replace_nodes(node.nodelist_loop)

    def find_node(self, nodes, block_name):
        for node in nodes:
            if isinstance(node, BlockNode) and node.name == block_name:
                return node
            
            ret = None
            if hasattr(node, 'nodelist'):
                ret = self.find_node(node.nodelist, block_name)
            elif hasattr(node, 'nodelist_loop'):
                ret = self.find_node(node.nodelist_loop, block_name)

            if ret:
                return ret
            
    def compile_nodelist(self):
        if register not in self.engine.template_builtins:
            self.engine.template_builtins += [register]

        ret = super().compile_nodelist()
        self.replace_nodes(ret)
        
        if self.filter_nodes:
            code_blocks = []
            for block in ret:
                if not hasattr(block, 'name'):
                    continue
                if block.name in self.filter_nodes:
                    code_blocks.append(block)
            return NodeList(code_blocks)

        if self.one_node:
            return NodeList([self.find_node(ret, self.one_node)])
        
        return ret

def compile_call_template(template):
    return CodeTemplate(template, one_node='call')

def render_call_template(compiled_template, input_data):
    return compiled_template.render(Context({'t': {'input': input_data}}, autoescape=False)).strip()

def compile_result_template(template):
    return CodeTemplate(template, one_node='result')

def render_result_template(compiled_template, answer_data):
    return compiled_template.render(Context({'t': {'answer': answer_data}}, autoescape=False)).strip()

def compile_assert_template(template):
    return CodeTemplate(template, one_node='tests')

def render_assert_template(compiled_template, input_data, answer_data):
    return compiled_template.render(Context({'tests': [
        {'input': input_data, 'answer': answer_data}]}, autoescape=False)).strip()
