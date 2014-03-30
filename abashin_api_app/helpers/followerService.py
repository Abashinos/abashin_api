from abashin_api_app import dbService
from StringBuilder import *

def listFollowersOrFollowees(data, mode, db=dbService.connect()):

    cur = db.cursor()
    cur.execute("""SELECT * FROM user
                   WHERE email = '%s'""" % data['user'])
    user = cur.fetchone()
    cur.close()

    if not user or len(user) == 0:
        raise Exception('No such user found')

    query = StringBuilder()

    if mode[1] == 'long':
        query.append("""SELECT *""")
    else:
        query.append("""SELECT email""")

    query.append(""" FROM user
                  WHERE email in""")
    if mode[0] == 'followers':
        query.append (""" (SELECT follower
                    FROM followers
                    WHERE followee = '%s' AND isFollowing = 1)""" % user['email'])
    else:
        query.append (""" (SELECT followee
                    FROM followers
                    WHERE follower = '%s' AND isFollowing = 1)""" % user['email'])

    if 'since_id' in data:
        query.append(""" AND id >= %s""" % data['since_id'])
    if mode[1] == 'long':
        query.append(""" ORDER BY name %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    cur = db.cursor()
    cur.execute(str(query))
    if mode[1] == 'long':
        users = cur.fetchall()
    else:
        temp_users = cur.fetchall()
        users = []
        for user in temp_users:
            users.append(user['email'])

    cur.close()

    return users
