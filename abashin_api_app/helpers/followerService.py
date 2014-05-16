from abashin_api_app import dbService
from abashin_api_app.helpers.subscriptionService import listSubscriptions
from abashin_api_app.services.StringBuilder import *


def listFollowersOrFollowees(data, mode, db=dbService.connect()):

    query = StringBuilder()
    params = ()

    if mode[1] == 'long':
        query.append("""SELECT *""")
    else:
        query.append("""SELECT email""")

    query.append(""" FROM user
                  WHERE email in""")
    if mode[0] == 'followers':
        query.append(""" (SELECT follower
                    FROM followers
                    WHERE followee = %s AND isFollowing = 1)""")
        params += (data['user'],)
    else:
        query.append(""" (SELECT followee
                    FROM followers
                    WHERE follower = %s AND isFollowing = 1)""")
        params += (data['user'],)

    if 'since_id' in data:
        query.append(""" AND id >= %s""")
        params += (data['since_id'],)
    if mode[1] == 'long':
        query.append(""" ORDER BY name %s""" % data['order'])

    if 'limit' in data:
        query.append(""" LIMIT %s""" % data['limit'])

    cur = db.cursor()
    cur.execute(str(query), params)
    if mode[1] == 'long':
        users = cur.fetchall()
        for user in users:
            user['subscriptions'] = listSubscriptions(user['email'], db)
            temp_user = {'user' : user['email']}
            user['followers'] = listFollowersOrFollowees(temp_user, ['followers', 'short'], db)
            user['following'] = listFollowersOrFollowees(temp_user, ['followees', 'short'], db)
    else:
        temp_users = cur.fetchall()
        users = []
        for user in temp_users:
            users.append(user['email'])

    cur.close()

    return users
