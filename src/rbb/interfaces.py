def unimplemented(method):
    method.unimplemented = False
    return method

def is_implemented(method):
    return not hasattr(method, "unimplemented")
