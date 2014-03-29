
def check_required_params(kwargs, params):
    for param in params:
        if param not in kwargs:
            raise Exception("Parameter '%s' is required" % param)


def check_optional_param(kwargs, param, default):
    if param not in kwargs:
        kwargs[param] = default



