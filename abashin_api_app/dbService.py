import MySQLdb, MySQLdb.cursors


def connect():
    db = MySQLdb.connect(host='localhost', port=3306, db='dbms',
                         user='test_user', passwd='test_pass',
                         charset='utf8',
                         cursorclass=MySQLdb.cursors.SSDictCursor)
    return db


def clear():
    db = connect()

    cur = db.cursor()
    cur.execute("set FOREIGN_KEY_CHECKS=0")
    cur.execute("TRUNCATE TABLE subscription")
    cur.execute("TRUNCATE TABLE followers")
    cur.execute("TRUNCATE TABLE post")
    cur.execute("TRUNCATE TABLE thread")
    cur.execute("TRUNCATE TABLE forum")
    cur.execute("TRUNCATE TABLE user")
    cur.execute("set FOREIGN_KEY_CHECKS=1")
    cur.close()

    db.close()

    pass
