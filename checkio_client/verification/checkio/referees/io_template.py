import os
from functools import cached_property

from .io import CheckiOReferee as BaseCheckiOReferee
from .. import api
from ..code_template import (
    compile_call_template, render_call_template, compile_result_template, render_result_template,
    compile_assert_template, render_assert_template)

class CheckiOReferee(BaseCheckiOReferee):
    @cached_property
    def code_template_file_name(self):
        return os.path.join(os.getenv('FOLDER_USER'), '..', 'editor', 'initial_code', 'python_3.tmpl')

    @cached_property
    def code_template_file_exist(self):
        os.path.exists(self.code_template_file_name)

    @cached_property
    def str_code_template(self):
        with open(self.code_template_file_name) as fh:
            return fh.read()

    @cached_property
    def call_template(self):
        return compile_call_template(self.str_code_template)

    @cached_property
    def result_template(self):
        return compile_result_template(self.str_code_template)
    
    @cached_property
    def assert_template(self):
        return compile_assert_template(self.str_code_template)

    def start_env_params(self):
        kwargs = super().start_env_params()
        kwargs['write_execute_data'] = False
        return kwargs

    def execute_current_test(self):
        api.request_write_in(self.current_test["input"], extra={
            'assert': render_assert_template(self.assert_template, self.current_test["input"], self.current_test["answer"]),
            'call': render_call_template(self.call_template, self.current_test["input"]),
            'answer': render_result_template(self.result_template, self.current_test["answer"]),
        })
        super().execute_current_test()

    def check_user_answer(self, result):
        ret = super().check_user_answer(result)

        api.request_write_out(result, extra={
            'answer': render_result_template(self.result_template, result),
            'correct': ret[0],
        })

        return ret

