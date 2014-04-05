import re
from abashin_api_app.entities import forum, user, thread, post


def execute(entity_name, method, request_data):

    entity = {
        "forum": forum,
        "user": user,
        "thread": thread,
        "post": post
    }[entity_name]

    method = re.sub('/', '', method)
    func_execution = getattr(entity, method)

    try:
        execution_result = func_execution(**request_data)
        response = {
            'code': 0,
            'response': execution_result
        }
    except Exception as e:
        response = {
            'code': 1,
            'response': str(e)
        }

    return response



