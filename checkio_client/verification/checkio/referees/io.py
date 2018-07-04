from checkio.signals import PROCESS_ENDED
from checkio import api
from checkio.api import DEFAULT_FUNCTION

from checkio.runner_types import SIMPLE, JS_RUNNER_SLUG


REQ = 'req'
REFEREE = 'referee'


class CheckiOReferee(object):
    current_category_index = 0
    current_category = "Undefined"
    current_test = {}
    current_step = 0
    current_test_index = 0
    tests = None
    restarting_env = False

    def __init__(self,
                 tests,
                 cover_code=None,
                 checker=None,
                 inspector=None,
                 add_close_builtins=None,
                 add_allowed_modules=None,
                 remove_allowed_modules=None,
                 function_name=DEFAULT_FUNCTION):

        self.tests = tests
        self.categories_names = sorted(list(tests.keys()))
        self.checker = checker
        self.inspector = inspector
        self.add_close_builtins = add_close_builtins
        self.add_allowed_modules = add_allowed_modules
        self.remove_allowed_modules = remove_allowed_modules
        self.cover_code = cover_code or {}
        self.function_name = function_name

    def on_ready(self, data):
        self.seed = data.get('seed', 0)
        self.code = data['code']
        self.runner = data['runner']

        if hasattr(self, 'function_name') and isinstance(self.function_name, dict):
            self.function_name = self.function_name[
                {
                    'python-27': 'python',
                    'python-3': 'python',
                    'js-node': 'js'
                }
                [self.runner]
            ]

        self.start_env()
        api.add_process_listener(REQ, PROCESS_ENDED, self.process_req_ended)

    def start_env(self):
        api.start_runner(code=self.code,
                         runner=self.runner,
                         prefix=REQ,
                         controller_type=SIMPLE,
                         callback=self.run_success,
                         errback=self.run_fail,
                         add_close_builtins=self.add_close_builtins,
                         add_allowed_modules=self.add_allowed_modules,
                         remove_allowed_modules=self.remove_allowed_modules,
                         write_execute_data=True,
                         cover_code=self.cover_code.get(self.runner))

    def run_success(self, data):
        self.current_category = self.get_current_env_name()
        api.request_write_start_in(self.current_category)

        self.current_step += 1
        self.test_current_step()

    def run_fail(self, data):
        api.fail(self.current_step)

    def test_current_step(self):
        self.current_test = self.get_current_test()
        api.execute_function(input_data=self.current_test["input"],
                             callback=self.check_current_test,
                             errback=self.fail_cur_step,
                             func=self.function_name)

    def get_current_env_name(self):
        return self.categories_names[self.current_category_index]

    def get_current_test(self):
        return self.tests[self.current_category][self.current_test_index]

    def check_current_test(self, data):
        if self.inspector:
            inspector_result, inspector_result_addon = self.inspector(self.code, self.runner)
            self.inspector = None
            self.current_test["inspector_result_addon"] = inspector_result_addon
            if not inspector_result:
                self.current_test["inspector_fail"] = True
                api.request_write_ext(self.current_test)
                return api.fail(0, inspector_result_addon)
        user_result = data['result']

        check_result = self.check_user_answer(user_result)
        self.current_test["result"], self.current_test["result_addon"] = check_result

        api.request_write_ext(self.current_test)

        if not self.current_test["result"]:
            return api.fail(self.current_step, self.get_current_test_fullname())

        if self.next_step():
            self.test_current_step()
        else:
            if self.next_env():
                self.restart_env()
            else:
                api.success()

    def check_user_answer(self, result):
        if self.checker:
            return self.checker(self.current_test["answer"], result)
        else:
            return self.current_test["answer"] == result, None

    def next_step(self):
        self.current_step += 1
        self.current_test_index += 1
        return self.current_test_index < len(self.tests[self.current_category])

    def next_env(self):
        self.current_category_index += 1
        self.current_test_index = 0
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
        try:
            tests_len = len(self.tests[self.current_category])
        except KeyError:
            tests_len = 0

        return "Category: {0}. Test {1} from {2}".format(
            self.current_category,
            self.current_test_index + 1,
            tests_len)
