def inspect_max_length(max_length):
    def inspector(code, runner=None):
        if len(code) > max_length:
            return (False,
                    "The code is too long. It must be shorter than {0} symbols".format(max_length))
        return True, None
    return inspector