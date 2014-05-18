from abashin_api_app import dbService
from abashin_api_app.entities import user
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
    forum_id = cur.lastrowid
    db.commit()
    cur.close()
    db.close()

    forum = {
        'id': forum_id,
        'name': data['name'],
        'short_name': data['short_name'],
        'user': data['user']
    }

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

    if not forum or len(forum) == 0:
        raise Exception("No forum found")

    if 'related' in data and len(data['related']) != 0 and data['related'] == 'user':
        user_data = {'user': forum['user']}
        forum['user'] = user.details(db, False, **user_data)

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

    db.close()
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

    for thread_data in threads:
        thread_data['isDeleted'] = bool(thread_data['isDeleted'])
        thread_data['isClosed'] = bool(thread_data['isClosed'])
        thread_data['date'] = thread_data['date'].strftime("%Y-%m-%d %H:%M:%S")

        if 'related' in data:
            if 'user' in data['related']:
                user_data = {'user': thread_data['user']}
                user_data = user.details(db, False, **user_data)
                thread_data['user'] = user_data
            if 'forum' in data['related']:
                forum_data = {'forum': thread_data['forum']}
                forum_data = details(db, False, **forum_data)
                thread_data['forum'] = forum_data

    db.close()

    return threads


def listUsers(**data):

    check_required_params(data, ['forum'])
    check_optional_param(data, 'order', 'desc')

    query = StringBuilder()
    params = ()
    query.append("""SELECT id, username, name, about, email, isAnonymous,
                   GROUP_CONCAT(DISTINCT thread ORDER BY thread separator ' ') AS subscriptions,
                   GROUP_CONCAT(DISTINCT fr.follower ORDER BY fr.follower separator ' ') AS followers,
                   GROUP_CONCAT(DISTINCT fe.followee ORDER BY fe.followee separator ' ') AS following
                   FROM user LEFT JOIN subscription
                   ON subscription.user = user.email AND isSubscribed = 1
                   LEFT JOIN followers AS fr
                   ON fr.followee = user.email AND fr.isFollowing = 1
                   LEFT JOIN followers AS fe
                   ON fe.follower = user.email AND fe.isFollowing = 1
                   WHERE email in (SELECT user from post
                   WHERE forum = %s)""")
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
    db.close()

    for user_data in users:
        if user_data['email']:
            if not user_data['subscriptions']:
                user_data['subscriptions'] = []
            else:
                user_data['subscriptions'] = [int(n) for n in user_data['subscriptions'].split()]

            if not user_data['followers']:
                user_data['followers'] = []
            else:
                user_data['followers'] = user_data['followers'].split()
            if not user_data['following']:
                user_data['following'] = []
            else:
                user_data['following'] = user_data['following'].split()

            user_data['isAnonymous'] = bool(user_data['isAnonymous'])
        else:
            users = []

    return users
