
from abashin_api_app import dbService
from abashin_api_app.entities import user, thread, forum
from abashin_api_app.services.StringBuilder import StringBuilder
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param


def create(**data):

    check_required_params(data, ['date', 'thread', 'message', 'user', 'forum'])
    check_optional_param(data, 'parent', None)
    check_optional_param(data, 'isApproved', False)
    check_optional_param(data, 'isHighlighted', False)
    check_optional_param(data, 'isEdited', False)
    check_optional_param(data, 'isSpam', False)
    check_optional_param(data, 'isDeleted', False)

    db = dbService.connect()
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO post (date, thread, message, user, forum, parent,
                                     isApproved, isHighlighted, isEdited, isSpam, isDeleted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (data['date'], data['thread'], data['message'], data['user'], data['forum'],
                    data['parent'], int(data['isApproved']), int(data['isHighlighted']), int(data['isEdited']),
                    int(data['isSpam']), int(data['isDeleted']),))
        post_id = cur.lastrowid
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.execute("""UPDATE thread
                   SET posts = posts + 1
                   WHERE id = %s""", (data['thread'],))
    db.commit()
    cur.close()
    db.close()

    post = {
        'id': post_id,
        'date': data['date'],
        'forum': data['forum'],
        'isApproved': data['isApproved'],
        'isDeleted': data['isDeleted'],
        'isEdited': data['isEdited'],
        'isHighlighted': data['isHighlighted'],
        'isSpam': data['isSpam'],
        'message': data['message'],
        'thread': data['thread'],
        'user': data['user']
    }
    return post


def details(db=0, close_db=True, **data):

    check_required_params(data, ['post'])

    if db == 0:
        db = dbService.connect()
    cur = db.cursor()
    cur.execute("""SELECT * FROM post
                   WHERE id = %s""", (data['post'],))
    post = cur.fetchone()
    cur.close()

    if not post or len(post) == 0:
        raise Exception("No post found")

    post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")

    if 'related' in data:
        if 'user' in data['related']:
            post['user'] = user.details(db, False, **post)
        if 'thread' in data['related']:
            post['thread'] = thread.details(db, False, **post)
        if 'forum' in data['related']:
            short_name = {'forum': post['forum']}
            post['forum'] = forum.details(db, False, **short_name)

    if close_db:
        db.close()

    return post


def list(**data):

    check_optional_param(data, 'order', 'desc')

    if 'thread' not in data and 'forum' not in data:
        raise Exception("thread or forum is required")
    if 'thread' in data and 'forum' in data:
        raise Exception("choose either thread or forum")

    query = StringBuilder()
    params = ()

    if 'thread' in data:
        query.append("""SELECT * FROM post
                       WHERE thread = %s""")
        params += (data['thread'],)
    elif 'forum' in data:
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
    db.close()

    for post in posts:
        post['date'] = post['date'].strftime("%Y-%m-%d %H:%M:%S")

    return posts


def remove(**data):

    check_required_params(data, ['post'])

    db = dbService.connect()

    cur = db.cursor()
    try:
        cur.execute("""UPDATE post
                       SET isDeleted = 1
                       WHERE id = %s""", (data['post'],))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'post': data['post']}


def restore(**data):

    check_required_params(data, ['post'])

    db = dbService.connect()

    cur = db.cursor()
    try:
        cur.execute("""UPDATE post
                       SET isDeleted = 0
                       WHERE id = %s""", (data['post'],))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()
    db.close()

    return {'post': data['post']}


def update(**data):

    check_required_params(data, ['post', 'message'])

    db = dbService.connect()

    cur = db.cursor()
    try:
        cur.execute("""UPDATE post
                       SET message = %s
                       WHERE id = %s""", (data['message'], data['post'],))
        db.commit()
    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        raise e

    cur.close()

    post = details(db, True, **data)

    return post


def vote(**data):

    check_required_params(data, ['post', 'vote'])

    data['vote'] = int(data['vote'])

    if data['vote'] != -1 and data['vote'] != 1:
        raise Exception("Illegal vote.")

    db = dbService.connect()
    cur = db.cursor()
    try:
        if data['vote'] == -1:
            cur.execute("""UPDATE post
                           SET dislikes = dislikes + 1,
                               points = points - 1
                           WHERE id = %s""", (data['post'],))
        else:
            cur.execute("""UPDATE post
                           SET likes = likes + 1,
                               points = points + 1
                           WHERE id = %s""", (data['post'],))
        db.commit()
    except Exception as e:
        cur.close()
        db.rollback()
        db.close()
        raise e

    cur.close()

    post = details(db, True, **data)

    return post
