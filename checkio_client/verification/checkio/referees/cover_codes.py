unwrap_args = '''

def cover(func, in_data):
    return func(*in_data)

'''

unwrap_kwargs = '''

def cover(func, in_data):
    return func(**in_data)

'''

js_unwrap_args = '''

function cover(func, in_data) {
    return func.apply(this, in_data)
}

'''
