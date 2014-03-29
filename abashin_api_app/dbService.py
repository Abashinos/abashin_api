import MySQLdb, MySQLdb.cursors

def connect():
    db = MySQLdb.connect(host='localhost', port=3306, db='dbms',
                         user='test_user', passwd='test_pass',
                         cursorclass=MySQLdb.cursors.SSDictCursor)
    return db
