from abashin_api_app import dbService
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def create(**data):

    check_required_params(data, ['name', 'short_name', 'user'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT id
                   FROM user
                   WHERE email = %s""", data['user'])
    user_id = cur.fetchone()
    cur.close()

#TODO: RETURN DETAILS
    return user_id