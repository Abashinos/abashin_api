from abashin_api_app import dbService
from abashin_api_app.services.paramChecker import *


def create(**data):

    check_required_params(data, ['email', 'username', 'name', 'about', 'password'])
    check_optional_param(data, 'isAnonymous', False)

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO user (email, username, password, name, about, isAnonymous)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                   (data['email'], data['username'], data['password'], data['name'], data['about'],
                    int(data['isAnonymous'])))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cur.close()
        db.close()

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM user
                   WHERE email=%s""",
               (data['email']))
    user = cur.fetchone()

    user['isAnonymous'] = bool(user['isAnonymous'])
    cur.close()
    db.close()

    return user

def details(**data):

    if 'user' not in data:
        raise Exception("parameter 'user' is required")

    db = dbService.connect()
    cur = db.cursor()

#TODO: Subscriptions, followers
    cur.execute("""SELECT id, about, email, username, name, isAnonymous
                   FROM user WHERE email = %s""", data['user'])
    user = cur.fetchone()

    if not user or len(user) == 0:
        raise Exception("No user found")

    user['isAnonymous'] = bool(user['isAnonymous'])

    cur.close()
    db.close()

    return user




