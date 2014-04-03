from abashin_api_app import dbService
from abashin_api_app.helpers import followerService
from abashin_api_app.helpers.subscriptionService import listSubscriptions
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def create(**data):

    check_required_params(data, ['name', 'short_name', 'user'])

    db = dbService.connect()

    cur = db.cursor()
    cur.execute("""INSERT INTO forum
                   (name, short_name, user)
                   VALUES (%s, %s, %s)""",
                (data['name'], data['short_name'], data['user'],))
    db.commit()
    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT *
                   FROM forum
                   WHERE short_name = %s""", (data['short_name'],))
    forum = cur.fetchone()
    cur.close()
    db.close()

    return forum


def details(**data):

    if 'short_name' not in data:
        raise Exception("parameter 'short_name' is required")

    db = dbService.connect()
    cur = db.cursor()

    cur.execute("""SELECT *
                   FROM forum
                   WHERE short_name = %s""", (data['short_name'],))
    forum = cur.fetchone()
    cur.close()

    data['user'] = forum['user']

    if 'related' in data and len(data['related']) != 0:
        cur = db.cursor()

        cur.execute("""SELECT id, email, isAnonymous, name
                       FROM user
                       WHERE email = %s""", (data['user'],))
        user_data = cur.fetchone()
        cur.close()

        user_data['subscriptions'] = listSubscriptions(data['user'], db)
        user_data['followers'] = followerService.listFollowersOrFollowees(data, ['followers', 'short'], db)
        user_data['following'] = followerService.listFollowersOrFollowees(data, ['followees', 'short'], db)
        user_data['isAnonymous'] = bool(user_data['isAnonymous'])
        forum['user'] = user_data

    db.close()

    return forum
