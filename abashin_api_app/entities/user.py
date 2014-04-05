from abashin_api_app import dbService
from abashin_api_app.helpers import followerService
from abashin_api_app.helpers.subscriptionService import listSubscriptions
from abashin_api_app.services.StringBuilder import StringBuilder
from abashin_api_app.services.paramChecker import *


def create(**data):

    check_required_params(data, ['email', 'username', 'name', 'about'])
    check_optional_param(data, 'isAnonymous', False)

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO user (email, username, name, about, isAnonymous)
                       VALUES (%s, %s, %s, %s, %s)""",
                   (data['email'], data['username'], data['name'], data['about'],
                    int(data['isAnonymous']),))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT about, email, id, isAnonymous, name, username
                   FROM user
                   WHERE email = %s""",
               (data['email'],))
    user = cur.fetchone()

    user['isAnonymous'] = bool(user['isAnonymous'])
    cur.close()
    db.close()

    return user


def details(db=0, close_db=True, **data):

    if 'user' not in data:
        raise Exception("parameter 'user' is required")

    if db == 0:
        db = dbService.connect()

    cur = db.cursor()
    cur.execute("""SELECT *
                   FROM user WHERE email = %s""", (data['user'],))
    user = cur.fetchone()
    cur.close()

    user['subscriptions'] = listSubscriptions(data['user'], db)
    user['followers'] = followerService.listFollowersOrFollowees(data, ['followers', 'short'], db)
    user['following'] = followerService.listFollowersOrFollowees(data, ['followees', 'short'], db)

    if not user or len(user) == 0:
        raise Exception("No user found")

    user['isAnonymous'] = bool(user['isAnonymous'])

    if close_db:
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
                   WHERE follower = %s AND followee = %s""", (data['follower'], data['followee'],))
    exists = cur.fetchone()
    cur.close()

    cur = db.cursor()
    try:
        if not exists or len(exists) == 0:
            cur.execute("""INSERT INTO followers
                           VALUES (%s, %s, 1)""", (data['follower'], data['followee'],))
        else:
            cur.execute("""UPDATE followers
                           SET isFollowing = 1
                           WHERE follower = %s AND followee = %s""", (data['follower'], data['followee'],))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()

    user = {'user': data['follower']}
    user = details(db, **user)

    return user


def unfollow(**data):

    check_required_params(data, ['follower', 'followee'])
    db = dbService.connect()
    cur = db.cursor()

    cur.execute("""SELECT * FROM followers
                   WHERE follower = %s AND followee = %s""", (data['follower'], data['followee'],))
    exists = cur.fetchone()
    cur.close()


    if exists and len(exists) != 0:
        try:
            cur = db.cursor()
            cur.execute("""UPDATE followers
                           SET isFollowing = 0
                           WHERE follower = %s AND followee = %s""", (data['follower'], data['followee'],))
            db.commit()
        except Exception as e:
            cur.close()
            db.rollback()
            db.close()
            raise e
        cur.close()

    user = {'user': data['follower']}
    user = details(db, **user)

    return user


def updateProfile(**data):

    check_required_params(data, ['about', 'user', 'name'])

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""UPDATE user
                       SET about = %s, name = %s
                       WHERE email = %s""",
                    (data['about'], data['name'], data['user'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()

    user = details(db, **data)

    return user


def listPosts(**data):

    check_required_params(data, ['user'])
    check_optional_param(data, 'order', 'desc')

    query = StringBuilder()
    params = ()
    query.append("""SELECT * FROM post
                    WHERE user = %s""")
    params += (data['user'],)

    if 'since' in data:
        query.append(""" AND date >= %s""")
        params += (data['since'],)

    query.append(""" ORDER BY date %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute(str(query), params)
    posts = cur.fetchall()
    cur.close()
    db.close()

    for post in posts:
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")
        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])

    return posts
