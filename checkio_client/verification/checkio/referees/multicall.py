from checkio.signals import PROCESS_ENDED
from checkio import api
from checkio.api import DEFAULT_FUNCTION

from checkio.runner_types import SIMPLE

REQ = 'req'
REFEREE = 'referee'


class CheckiORefereeMulti(object):
    current_category_index = 0
    current_category = ""
    current_step = 0
    restarting_env = False

    def __init__(self,
                 tests,
                 initial_referee,
                 process_referee,
                 is_win_referee,
                 cover_code=None,
                 inspector=None,
                 add_close_builtins=None,
                 add_allowed_modules=None,
                 remove_allowed_modules=None,
                 function_name=DEFAULT_FUNCTION):

        self.tests = tests
        self.initial_referee = initial_referee
        self.process_referee = process_referee
        self.is_win_referee = is_win_referee
        self.categories_names = sorted(list(tests.keys()))
        self.inspector = inspector
        self.add_close_builtins = add_close_builtins
        self.add_allowed_modules = add_allowed_modules
        self.remove_allowed_modules = remove_allowed_modules
        self.cover_code = cover_code or {}
        self.function_name = function_name

        self.referee_data = {
            "input": "",
            "result": "",
            "result_addon": ""
        }

    def on_ready(self, data):
        self.code = data['code']
        self.runner = data['runner']
        if self.inspector:
            result, result_message = self.inspector(self.code, self.runner)
            if not result:
                api.fail(0, result_message)
        self.start_env()

        api.add_process_listener(REQ, PROCESS_ENDED, self.process_req_ended)

    def start_env(self):
        api.start_runner(code=self.code,
                         runner=self.runner,
                         prefix=REQ,
                         controller_type=SIMPLE,
                         callback=self.run_success,
                         errback=self.fail_cur_step,
                         add_close_builtins=self.add_close_builtins,
                         add_allowed_modules=self.add_allowed_modules,
                         remove_allowed_modules=self.remove_allowed_modules,
                         write_execute_data=True,
                         cover_code=self.cover_code.get(self.runner))

    def run_success(self, data):
        self.current_step = 0
        self.current_category = self.get_current_env_name()
        api.request_write_start_in(self.current_category)
        self.referee_data = self.initial_referee(self.tests[self.current_category])

        self.test_current_step()

    def test_current_step(self):
        self.current_step += 1
        api.execute_function(input_data=self.referee_data["input"],
                             callback=self.check_current_test,
                             errback=self.fail_cur_step,
                             func=self.function_name)

    def get_current_env_name(self):
        return self.categories_names[self.current_category_index]

    def check_current_test(self, data):
        user_result = data['result']

        self.referee_data = self.process_referee(self.referee_data, user_result)

        referee_result = self.referee_data.get("result", False)

        is_win_result = False

        if referee_result:
            is_win_result = self.is_win_referee(self.referee_data)

        self.referee_data.update({"is_win": is_win_result})

        api.request_write_ext(self.referee_data)

        if not referee_result:
            return api.fail(self.current_step, self.get_current_test_fullname())

        if not is_win_result:
            self.test_current_step()
        else:
            if self.next_env():
                self.restart_env()
            else:
                api.success()

    def next_env(self):
        self.current_category_index += 1
        return self.current_category_index < len(self.categories_names)

    def restart_env(self):
        self.restarting_env = True
        api.kill_runner('req')

    def process_req_ended(self, data):
        if self.restarting_env:
            self.restarting_env = False
            self.start_env()
        else:
            api.fail(self.current_step, self.get_current_test_fullname())

    def fail_cur_step(self, data):
        api.fail(self.current_step, self.get_current_test_fullname())

    def get_current_test_fullname(self):
        return "Test: {0}. Step {1}".format(
            self.current_category,
            self.current_step)
