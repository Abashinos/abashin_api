
from abashin_api_app import dbService
from abashin_api_app.entities import user, thread, forum
from abashin_api_app.services.paramChecker import check_required_params, check_optional_param

def create(**data):

    check_required_params(data, ['date', 'thread', 'message', 'user', 'forum'])
    check_optional_param(data, 'parent', None)
    check_optional_param(data, 'isApproved', False)
    check_optional_param(data, 'isHighlited', False)
    check_optional_param(data, 'isEdited', False)
    check_optional_param(data, 'isSpam', False)
    check_optional_param(data, 'isDeleted', False)

    db = dbService.connect()
    cur = db.cursor()
    cur.execute("""INSERT INTO post (date, thread, message, user, forum, parent
                                     isApproved, isHighlighted, isEdited, isSpam, isDeleted)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (data['date'], data['thread'], data['message'], data['user'], data['forum'],
         data['parent'], int(data['isApproved']), int(data['isHighlighted']), int(data['isEdited']),
         int(data['isSpam']), int(data['isDeleted']),))
    cur.close()

    #TODO: return post


def details(db=dbService.connect(), **data):

    check_required_params(data, ['post'])

    cur = db.cursor()
    cur.execute("""SELECT * FROM post
                   WHERE id = %s""", (data['post'],))
    post = cur.fetchone()
    cur.close()

    if 'related' in data:
        if 'user' in data['related']:
            post['user'] = user.details(db, **post)
        if 'thread' in data['related']:
            post['thread'] = thread.details(db, **post)
        if 'forum' in data['related']:
            post['forum'] = forum.details(db, **post)

    db.close()

    return post


