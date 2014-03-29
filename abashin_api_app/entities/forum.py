from abashin_api_app import dbService
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def create(**data):

    check_required_params(data, ['name', 'short_name', 'user'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT id
                   FROM user
                   WHERE email = %s""", data['user'])
    user_id = cur.fetchone()['id']
    cur.close()

    cur = db.cursor()
    cur.execute("""INSERT INTO forum
                   (name, short_name, user_id, user)
                   VALUES (%s, %s, %s, %s)""",
                (data['name'], data['short_name'], user_id, data['user']))
    db.commit()

    cur.close()
    db.close()

    return details(db, data)


def details(db=dbService.connect(), **data):

    if 'short_name' not in data:
        raise Exception("parameter 'short_name' is required")

    if 'related' not in data:
        data['related'] = []

    cur = db.cursor()

    cur.execute("""SELECT id, name, short_name
                   FROM forum
                   WHERE short_name = %s""", data['short_name'])
    forum = cur.fetchone()
    cur.close()

    #TODO: related

    return forum
