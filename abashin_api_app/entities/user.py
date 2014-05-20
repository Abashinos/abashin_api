from abashin_api_app import dbService
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
        _id = cur.lastrowid
        cur.fetchall()
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        cur.close()
        db.close()

    user = {
        'id': _id,
        'email': data['email'],
        'username': data['username'],
        'name': data['name'],
        'about': data['about'],
        'isAnonymous': data['isAnonymous']
    }

    return user


def details(db=0, close_db=True, **data):

    if 'user' not in data:
        raise Exception("parameter 'user' is required")

    if db == 0:
        db = dbService.connect()

    cur = db.cursor()
    cur.execute("""SELECT id, username, name, about, email, isAnonymous,
                   GROUP_CONCAT(DISTINCT thread ORDER BY thread separator ' ') AS subscriptions,
                   GROUP_CONCAT(DISTINCT fr.follower ORDER BY fr.follower separator ' ') AS followers,
                   GROUP_CONCAT(DISTINCT fe.followee ORDER BY fe.followee separator ' ') AS following
                   FROM user LEFT JOIN subscription
                   ON subscription.user = user.email
                   LEFT JOIN followers AS fr
                   ON fr.followee = user.email
                   LEFT JOIN followers AS fe
                   ON fe.follower = user.email
                   WHERE email = %s """, (data['user'],))
    user = cur.fetchone()
    cur.close()

    if not user or len(user) or user.email is None == 0:
        user = {}
    else:
        if not user['subscriptions']:
            user['subscriptions'] = []
        else:
            user['subscriptions'] = [int(n) for n in user['subscriptions'].split()]

        if not user['followers']:
            user['followers'] = []
        else:
            user['followers'] = user['followers'].split()
        if not user['following']:
            user['following'] = []
        else:
            user['following'] = user['following'].split()

        user['isAnonymous'] = bool(user['isAnonymous'])

    if close_db:
        db.close()

    return user


def listFollowers(**data):

    check_required_params(data, ['user'])
    if 'order' not in data:
        data['order'] = 'desc'

    query = StringBuilder()
    params = ()

    query.append("""SELECT id, username, name, about, email, isAnonymous,
                   GROUP_CONCAT(DISTINCT thread ORDER BY thread separator ' ') AS subscriptions,
                   GROUP_CONCAT(DISTINCT fr.follower ORDER BY fr.follower separator ' ') AS followers,
                   GROUP_CONCAT(DISTINCT fe.followee ORDER BY fe.followee separator ' ') AS following
                   FROM user LEFT JOIN subscription
                   ON subscription.user = user.email
                   LEFT JOIN followers AS fr
                   ON fr.followee = user.email
                   LEFT JOIN followers AS fe
                   ON fe.follower = user.email
                   WHERE email in (SELECT follower from followers
                   WHERE followee = %s) """)
    params += (data['user'],)

    if 'since_id' in data:
        query.append(""" AND id >= %s""")
        params += (data['since_id'],)

    query.append("""GROUP BY email ORDER BY name %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute(str(query), params)
    followers = cur.fetchall()
    cur.close()
    db.close()

    for user in followers:
        if user['email']:
            if not user['subscriptions']:
                user['subscriptions'] = []
            else:
                user['subscriptions'] = [int(n) for n in user['subscriptions'].split()]

            if not user['followers']:
                user['followers'] = []
            else:
                user['followers'] = user['followers'].split()
            if not user['following']:
                user['following'] = []
            else:
                user['following'] = user['following'].split()

            user['isAnonymous'] = bool(user['isAnonymous'])
        else:
            followers = []

    return followers


def listFollowing(**data):

    check_required_params(data, ['user'])
    if 'order' not in data:
        data['order'] = 'desc'

    query = StringBuilder()
    params = ()

    query.append("""SELECT id, username, name, about, email, isAnonymous,
                   GROUP_CONCAT(DISTINCT thread ORDER BY thread separator ' ') AS subscriptions,
                   GROUP_CONCAT(DISTINCT fr.follower ORDER BY fr.follower separator ' ') AS followers,
                   GROUP_CONCAT(DISTINCT fe.followee ORDER BY fe.followee separator ' ') AS following
                   FROM user LEFT JOIN subscription
                   ON subscription.user = user.email
                   LEFT JOIN followers AS fr
                   ON fr.followee = user.email
                   LEFT JOIN followers AS fe
                   ON fe.follower = user.email
                   WHERE email in (SELECT followee from followers
                   WHERE follower = %s) """)
    params += (data['user'],)

    if 'since_id' in data:
        query.append(""" AND id >= %s""")
        params += (data['since_id'],)

    query.append("""GROUP BY email ORDER BY name %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute(str(query), params)
    followees = cur.fetchall()
    cur.close()
    db.close()

    for user in followees:
        if user['email']:
            if not user['subscriptions']:
                user['subscriptions'] = []
            else:
                user['subscriptions'] = [int(n) for n in user['subscriptions'].split()]

            if not user['followers']:
                user['followers'] = []
            else:
                user['followers'] = user['followers'].split()
            if not user['following']:
                user['following'] = []
            else:
                user['following'] = user['following'].split()

            user['isAnonymous'] = bool(user['isAnonymous'])
        else:
            followees = []

    return followees


def follow(**data):

    check_required_params(data, ['follower', 'followee'])
    db = dbService.connect()
    cur = db.cursor()

    try:
        cur.execute("""INSERT INTO followers
                       VALUES (%s, %s)""", (data['follower'], data['followee'],))
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

    try:
        cur.execute("""DELETE FROM followers
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
