from abashin_api_app import dbService
from abashin_api_app.helpers import followerService
from abashin_api_app.services.paramChecker import *


def create(**data):

    check_required_params(data, ['email', 'username', 'name', 'about', 'password'])
    check_optional_param(data, 'isAnonymous', False)

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO user (email, username, password, name, about, isAnonymous)
                       VALUES (%s, %s, %s, %s, %s, %s)""" %
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
                   WHERE email=%s""" %
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

#TODO: Subscriptions
    cur.execute("""SELECT id, about, email, username, name, isAnonymous
                   FROM user WHERE email = %s""" % data['user'])
    user = cur.fetchone()
    cur.close()

    user['followers'] = followerService.listFollowersOrFollowees(data, ['followers', 'short'], db)
    user['following'] = followerService.listFollowersOrFollowees(data, ['followees', 'short'], db)

    if not user or len(user) == 0:
        raise Exception("No user found")

    user['isAnonymous'] = bool(user['isAnonymous'])

    db.close()

    return user


def listFollowers(**data):

    check_required_params(data, ['user'])
    if 'order' not in data:
        data['order'] = 'desc'

    db = dbService.connect()
    followers = followerService.listFollowersOrFollowees(data, ['followers', 'long'], db)
    db.close()

    return followers


def listFollowing(**data):

    check_required_params(data, ['user'])
    if 'order' not in data:
        data['order'] = 'desc'

    db = dbService.connect()
    followees = followerService.listFollowersOrFollowees(data, ['followees', 'long'], db)
    db.close()

    return followees


def follow(**data):

    check_required_params(data, ['follower', 'followee'])
    db = dbService.connect()
    cur = db.cursor()

    cur.execute("""SELECT * FROM followers
                   WHERE follower = %s AND followee = %s""" % (data['follower'], data['followee']))
    exists = cur.fetchone()
    cur.close()

    cur = db.cursor()
    try:
        if not exists or len(exists) == 0:
            cur.execute("""INSERT INTO followers
                           VALUES (%s, %s, 1)""" % (data['follower'], data['followee']))
        else:
            cur.execute("""UPDATE followers
                           SET isFollowing = 1
                           WHERE follower = %s AND followee = %s""" % (data['follower'], data['followee']))
        db.commit()
    except Exception as e:
        db.rollback()
        db.close()
        raise e

    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT * FROM user
                   WHERE email = '%s'""" % data['follower'])
    user = cur.fetchone()
    cur.close()
    db.close()

    return user


def unfollow(**data):

    check_required_params(data, ['follower', 'followee'])
    db = dbService.connect()
    cur = db.cursor()

    cur.execute("""SELECT * FROM followers
                   WHERE follower = %s AND followee = %s""" % (data['follower'], data['followee']))
    exists = cur.fetchone()
    cur.close()


    if exists and len(exists) != 0:
        try:
            cur = db.cursor()
            cur.execute("""UPDATE followers
                           SET isFollowing = 0
                           WHERE follower = %s AND followee = %s""" % (data['follower'], data['followee']))
            db.commit()
        except Exception as e:
            db.rollback()
            db.close()
            raise e
        finally:
            cur.close()

    cur = db.cursor()
    cur.execute("""SELECT * FROM user
                   WHERE email = '%s'""" % data['follower'])
    user = cur.fetchone()
    cur.close()
    db.close()

    return user



