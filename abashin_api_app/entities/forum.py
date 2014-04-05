from abashin_api_app import dbService
from abashin_api_app.helpers import followerService
from abashin_api_app.helpers.subscriptionService import listSubscriptions
from abashin_api_app.services.StringBuilder import StringBuilder
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


def details(db=0, close_db=True, **data):

    if 'forum' not in data:
        raise Exception("parameter 'forum' is required")

    if db == 0:
        db = dbService.connect()

    cur = db.cursor()

    cur.execute("""SELECT *
                   FROM forum
                   WHERE short_name = %s""", (data['forum'],))
    forum = cur.fetchone()
    cur.close()

    data['user'] = forum['user']

    if 'related' in data and len(data['related']) != 0 and data['related'] == 'user':
        cur = db.cursor()

        cur.execute("""SELECT id, email, isAnonymous, name
                       FROM user
                       WHERE email = %s""", (data['user'],))
        user_data = cur.fetchone()
        cur.close()

        user_data['isAnonymous'] = bool(user_data['isAnonymous'])
        user_data['subscriptions'] = listSubscriptions(data['user'], db)
        user_data['followers'] = followerService.listFollowersOrFollowees(data, ['followers', 'short'], db)
        user_data['following'] = followerService.listFollowersOrFollowees(data, ['followees', 'short'], db)

        forum['user'] = user_data

    if close_db:
        db.close()

    return forum


def listPosts(**data):
    from abashin_api_app.entities import thread, user

    check_required_params(data, ['forum'])
    check_optional_param(data, 'order', 'desc')

    query = StringBuilder()
    params = ()
    query.append("""SELECT * FROM post
                    WHERE thread in (SELECT id FROM thread WHERE forum = %s)""")
    params += (data['forum'],)

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

    for post in posts:
        post['isApproved'] = bool(post['isApproved'])
        post['isDeleted'] = bool(post['isDeleted'])
        post['isEdited'] = bool(post['isEdited'])
        post['isHighlighted'] = bool(post['isHighlighted'])
        post['isSpam'] = bool(post['isSpam'])
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")

        if 'related' in data:
            if 'thread' in data['related']:
                thread_data = {'thread': post['thread']}
                thread_data = thread.details(db, False, **thread_data)
                post['thread'] = thread_data
            if 'user' in data['related']:
                user_data = {'user': post['user']}
                user_data = user.details(db, False, **user_data)
                post['user'] = user_data
            if 'forum' in data['related']:
                forum_data = {'forum': post['forum']}
                forum_data = details(db, False, **forum_data)
                post['forum'] = forum_data

    return posts


def listThreads(**data):
    from abashin_api_app.entities import thread, user

    check_required_params(data, ['forum'])
    check_optional_param(data, 'order', 'desc')

    query = StringBuilder()
    params = ()
    query.append("""SELECT * FROM thread
                    WHERE forum = %s""")
    params += (data['forum'],)

    if 'since' in data:
        query.append(""" AND date >= %s""")
        params += (data['since'],)

    query.append(""" ORDER BY date %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute(str(query), params)
    threads = cur.fetchall()
    cur.close()

    for thread in threads:
        thread['isDeleted'] = bool(thread['isDeleted'])
        thread['isClosed'] = bool(thread['isClosed'])
        thread['date'] = thread['date'].strftime("%Y-%m-%d %H:%M:%S")

        if 'related' in data:
            if 'user' in data['related']:
                user_data = {'user': thread['user']}
                user_data = user.details(db, False, **user_data)
                thread['user'] = user_data
            if 'forum' in data['related']:
                forum_data = {'forum': thread['forum']}
                forum_data = details(db, False, **forum_data)
                thread['forum'] = forum_data

    return threads


def listUsers(**data):
    from abashin_api_app.entities import user

    check_required_params(data, ['forum'])
    check_optional_param(data, 'order', 'desc')

    query = StringBuilder()
    params = ()
    query.append("""SELECT * FROM user
                    WHERE email in
                    (SELECT user FROM post WHERE thread in
                    (SELECT id from thread WHERE forum = %s))""")
    params += (data['forum'],)

    if 'since_id' in data:
        query.append(""" AND id >= %s""")
        params += (data['since_id'],)

    query.append(""" ORDER BY id %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute(str(query), params)
    users = cur.fetchall()
    cur.close()

    for user in users:
        user['subscriptions'] = listSubscriptions(user['email'], db)
        user_data = {'user': user['email']}
        user['followers'] = followerService.listFollowersOrFollowees(user_data, ['followers', 'short'], db)
        user['following'] = followerService.listFollowersOrFollowees(user_data, ['followees', 'short'], db)
        user['isAnonymous'] = bool(user['isAnonymous'])
    return users
