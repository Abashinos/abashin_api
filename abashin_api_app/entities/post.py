from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def details(**data):

    check_required_params(data, ['post'])
