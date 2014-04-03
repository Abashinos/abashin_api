from abashin_api_app import dbService
from abashin_api_app.services.StringBuilder import StringBuilder
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def create(**data):

    check_required_params(data, ['forum', 'title', 'isClosed', 'user',
                                 'date', 'message', 'slug'])
    check_optional_param(data, 'isDeleted', False)

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO thread (forum, title, isClosed, isDeleted, user,
                                           date, message, slug, points)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)""",
                    (data['forum'], data['title'], data['isClosed'], data['isDeleted'],
                        data['user'], data['date'], data['message'], data['slug'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e
    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT id, date, forum, isClosed, isDeleted,
                          message, slug, title, user
                   FROM thread
                   WHERE slug = %s""", (data['slug'],))
    thread = cur.fetchone()
    cur.close()
    db.close()

    return thread


def details(**data):

    check_required_params(data, ['thread'])
    check_optional_param(data, 'related', [])

    db = dbService.connect()
    cur = db.cursor()

    #TODO: likes, points, posts
    cur.execute("""SELECT *
                   FROM thread
                   WHERE id = %s""", (data['thread'],))
    thread = cur.fetchone()
    cur.close()
    db.close()

    return thread


def close(**data):

    check_required_params(data, ['thread'])

    db = dbService.connect()
    cur = db.cursor()

    try:
        cur.execute("""UPDATE thread
                       SET isClosed = 1
                       WHERE id = %s""", (data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread']}


def list(**data):

    check_optional_param(data, 'order', 'desc')

    if 'user' not in data and 'forum' not in data:
        raise Exception("Either user or forum is required")
    if 'user' in data and 'forum' in data:
        raise Exception("You can choose user or forum, but not both")

    db = dbService.connect()

    query = StringBuilder()
    params = ()
    if 'user' in data:
        query.append("""SELECT *
                       FROM thread
                       WHERE user = %s""")
        params += (data['user'],)
    elif 'forum' in data:
        query.append("""SELECT *
                       FROM thread
                       WHERE forum = %s""")
        params += (data['forum'],)

    if 'since' in data:
        query.append(""" AND date >= %s""")
        params += (data['since'],)

    if 'order' in data:
        query.append(""" ORDER BY date %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    cur = db.cursor()
    cur.execute(str(query), params)
    list = cur.fetchall()
    cur.close()

    return list


def open(**data):

    check_required_params(data, ['thread'])

    db = dbService.connect()
    cur = db.cursor()

    try:
        cur.execute("""UPDATE thread
                       SET isClosed = 0
                       WHERE id = %s""", (data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread']}


def remove(**data):

    check_required_params(data, ['thread'])

    db = dbService.connect()
    cur = db.cursor()

    try:
        cur.execute("""UPDATE thread
                       SET isDeleted = 1
                       WHERE id = %s""", (data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread']}


def restore(**data):

    check_required_params(data, ['thread'])

    db = dbService.connect()
    cur = db.cursor()

    try:
        cur.execute("""UPDATE thread
                       SET isDeleted = 0
                       WHERE id = %s""", (data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread']}


def update(**data):

    check_required_params(data, ['message', 'slug', 'thread'])

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""UPDATE thread
                       SET message = %s, slug = %s
                       WHERE id = %s""",
                    (data['message'], data['slug'], data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT * FROM thread
                   WHERE id = %s""", (data['thread'],))
    thread = cur.fetchone()
    cur.close()
    db.close()

    return thread


def vote(**data):

    check_required_params(data, ['thread', 'vote'])

    data['vote'] = int(data['vote'])

    if data['vote'] != -1 and data['vote'] != 1:
        raise Exception("Illegal vote.")

    db = dbService.connect()
    cur = db.cursor()
    try:
        if data['vote'] == -1:
            cur.execute("""UPDATE thread
                           SET dislikes = dislikes + 1,
                               points = points - 1
                           WHERE id = %s""", (data['thread'],))
        else:
            cur.execute("""UPDATE thread
                           SET likes = likes + 1,
                               points = points + 1
                           WHERE id = %s""", (data['thread'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()

    cur = db.cursor()
    cur.execute("""SELECT * FROM thread
                   WHERE id = %s""", (data['thread'],))
    thread = cur.fetchone()
    cur.close()
    db.close()

    return thread


def subscribe(**data):

    check_required_params(data, ['thread', 'user'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT * FROM subscription
                   WHERE user = %s AND thread = %s""", (data['user'], data['thread'],))
    exists = cur.fetchone()
    cur.close()

    cur = db.cursor()
    try:
        if not exists or len(exists) == 0:
            cur.execute("""INSERT INTO subscription
                           VALUES (%s, %s, 1)""", (data['user'], data['thread'],))
        else:
            cur.execute("""UPDATE subscription
                           SET isSubscribed = 1
                           WHERE user = %s AND thread = %s""", (data['user'], data['thread'],))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread'], 'user': data['user']}


def unsubscribe(**data):

    check_required_params(data, ['thread', 'user'])

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT * FROM subscription
                   WHERE user = %s AND thread = %s""", (data['user'], data['thread'],))
    exists = cur.fetchone()
    cur.close()

    cur = db.cursor()
    try:
        if exists and len(exists) != 0:
            cur.execute("""UPDATE subscription
                           SET isSubscribed = 0
                           WHERE user = %s AND thread = %s""", (data['user'], data['thread'],))
            db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'thread': data['thread'], 'user': data['user']}
