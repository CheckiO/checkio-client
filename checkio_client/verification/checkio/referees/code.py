from checkio import api

from checkio.referees.io import CheckiOReferee

REQ = 'req'
REFEREE = 'referee'


class CheckiORefereeCode(CheckiOReferee):

    def __init__(self,
                 tests,
                 check_result=None,
                 inspector=None,
                 add_close_builtins=None,
                 add_allowed_modules=None,
                 remove_allowed_modules=None):

        self.tests = tests
        self.categories_names = sorted(list(tests.keys()))
        self.check_result = check_result
        self.inspector = inspector
        self.add_close_builtins = add_close_builtins
        self.add_allowed_modules = add_allowed_modules
        self.remove_allowed_modules = remove_allowed_modules
        self.cover_code = {}

    def test_current_step(self):
        self.current_test = self.get_current_test()
        self.current_test["runner"] = self.runner
        api.request_write_in(self.current_test["show"][self.runner], REQ)
        api.sys_runner(code=self.current_test["test_code"].get(self.runner),
                       callback=self.check_current_test,
                       errback=self.fail_cur_step)

    def check_current_test(self, data):

        if self.inspector:
            inspector_result, inspector_result_addon = self.inspector(self.code, self.runner)
            self.inspector = None
            self.current_test["inspector_result_addon"] = inspector_result_addon
            if not inspector_result:
                self.current_test["inspector_fail"] = True
                api.request_write_ext(self.current_test)
                return api.fail(0, inspector_result_addon)


        test_result = data["result"]
        self.current_test.update(test_result)
        check_result = self.check_user_answer(test_result)

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

    def check_user_answer(self, data):
        if self.check_result:
            return self.check_result(data, self.current_test)
        else:
            return self.current_test["answer"] == data.get("code_result", None), None
