
from flask import g

import sqlite3

connection = sqlite3.connect('db.sqlite')
print("bağlantı başarılı")

#with open('schema.sql') as f:
#    connection.executescript(f.read())

cur = connection.cursor()

#cur.execute("INSERT INTO posts (name, postName, postDescription, postLike) VALUES ('ali','denem postu','postun Açıklaması',12 )")
'''
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )
'''

deneme = cur.execute("""SELECT * FROM posts""")
#print(deneme.fetchall())

twoTable = cur.execute('SELECT posts.id, posts.name, posts.postDescription, postComment.commentPost, postComment.senderName FROM posts inner join postComment WHERE postComment.postID = posts.id')
twoTable = twoTable.fetchall()
print(twoTable)
connection.close()

'''
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
'''