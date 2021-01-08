from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_marshmallow import Marshmallow

import os
import warnings

#with warnings.catch_warnings():
#     from flask_marshmallow import Marshmallow

# Initialize App
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init marshmallow
ma = Marshmallow(app)



#Product Class/Model
class posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    postName = db.Column(db.String(100))
    postDescription = db.Column(db.String(500))
    postLike = db.Column(db.Integer)
    postTime = db.Column(db.String(50))

    #postR = db.relationship('postComment', backref='postComment.postID', primaryjoin='posts.id==postComments.postID', lazy='joined')

    def __init__(self, name, postName, postDescription, postLike, postTime):
        self.name = name
        self.postName = postName
        self.postDescription = postDescription
        self.postLike = postLike
        self.postTime = postTime

class postComment(db.Model):
    __tablename__ = "postComment"
    id = db.Column(db.Integer, primary_key=True)
    postID = db.Column(db.Integer)
    senderName = db.Column(db.String(20))
    commentPost = db.Column(db.String(300))
    commentTime = db.Column(db.String(300))


    def __init__(self, postID, senderName, commentPost, commentTime):
        self.postID = postID
        self.senderName = senderName
        self.commentPost = commentPost
        self.commentTime = commentTime

class mamaKaplari(db.Model):
    __tablename__ = "Mamalar"
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.String(100))
    latitude = db.Column(db.String(100))
    fillingTime = db.Column(db.String(100))

    def __init__(self, longitude, latitude, fillingTime):
        self.longitude = longitude
        self.latitude = latitude
        self.fillingTime = fillingTime

#posts Schema
class MamaSchema(ma.Schema):
    class Meta:
        fields = ('id','longitude','latitude','fillingTime')

class PostsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'postName', 'postDescription', 'postLike', 'postTime')

class CommentsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'postID', 'senderName', 'commentPost', 'commentTime')

class PostAndCommentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'postName', 'postDescription', 'postLike', 'postTime', 'commentPost', 'senderName', 'commentTime')

#Init Schema
mamakaplari_schema = MamaSchema()
mamakaplari_schema2 = MamaSchema(many=True)

posts_schema = PostsSchema()
posts_schema2 = PostsSchema(many=True)

postandcomment_schema = PostAndCommentSchema()
postandcomment_schema2 = PostAndCommentSchema(many=True)

comments_schema = CommentsSchema()
comments_schema2 = CommentsSchema(many=True)

# Create posts
@app.route('/posts', methods=['POST'])
def add_posts():
    name = request.json['name']
    postName = request.json['postName']
    postDescription = request.json['postDescription']
    postLike = request.json['postLike']
    postTime = request.json['postTime']

    new_posts = posts(name, postName, postDescription, postLike, postTime)
    print(new_posts)
    db.session.add(new_posts)
    db.session.commit()

    return posts_schema.jsonify(new_posts)


@app.route('/comments',methods=['POST'])
def comment_add():
    postID = request.json['postID']
    senderName = request.json['senderName']
    commentPost = request.json['commentPost']
    commentTime = request.json['commentTime']

    new_comment = postComment(postID, senderName, commentPost, commentTime)

    print(new_comment)
    db.session.add(new_comment)
    db.session.commit()

    return comments_schema.jsonify(new_comment)


@app.route('/mamaKaplari',methods=['POST'])
def mamakaplari_post():
    fillingTime = request.json['fillingTime']
    longitude = request.json['longitude']
    latitude = request.json['latitude']

    new_kaava = mamaKaplari(longitude, latitude, fillingTime)
    db.session.add(new_kaava)
    db.session.commit()

    return mamakaplari_schema.jsonify(new_kaava)

@app.route('/postLike',methods=['PUT'])
def post_like_post():

    connection = sqlite3.connect('db.sqlite')
    cur = connection.cursor()

    posts_id = int(request.json['id'])
    posts_like = int(request.json['postLike'])

    update = "UPDATE posts SET postLike = postLike + "+str(posts_like)+" WHERE id = " + str(posts_id)

    print(posts_id,posts_like)
    print("update : ", update)
    #cur.execute("""UPDATE posts SET postLike = postLike + ? WHERE id = ?""", (posts_id,posts_like,))
    cur.execute(update)
    connection.commit()

    update_like = cur.execute("""SELECT * FROM posts """)
    update_like = update_like.fetchall()
    connection.close()
    print(update_like)

    return jsonify(update_like)



@app.route('/mamaKaplari', methods=['GET'])
def mamakaplari_get():
        all_kaavas = mamaKaplari.query.all()
        result = mamakaplari_schema2.dump(all_kaavas)
        print(result)

        return jsonify(result)

@app.route('/post/<id>',methods=['GET'])
def get_one_post(id):
    gelen_post = posts.query.get(id)
    gelen_yorum = postComment.query.get(id)
    return posts_schema.jsonify(gelen_post), comments_schema.jsonify(gelen_yorum)

# Get All postss
@app.route('/posts', methods=['GET'])
def get_posts():
    all_posts = posts.query.all()
    all_comments = postComment.query.all()

    result = posts_schema2.dump(all_posts)
    #comment = comments_schema2.dump(all_comments)
    #return jsonify(result, comment)
    print(result)
    return jsonify(result)


'''
    fillingTime = request.json['fillingTime']
    longitude = request.json['longitude']
    latitude = request.json['latitude']
'''


@app.route('/postComments/<id>',methods=['GET'])
def get_comment_post(id):
    connection = sqlite3.connect('db.sqlite')
    cur = connection.cursor()
    comment_id = postComment.query.get(id)
    twoTable = cur.execute("""SELECT posts.id, posts.name, posts.postName, posts.postDescription, posts.postLike, posts.postTime, postComment.commentPost, postComment.senderName, commentTime FROM posts inner join postComment WHERE postComment.postID = posts.id AND posts.id = ? """,(id))
    twoTable = twoTable.fetchall()
    payload = []
    content = {}
    #for result in twoTable:
    #    content = {'id': result[0], 'name': result[1],'postName':result[2], 'postDescription':result[3],'postLike':result[4],'postTime':result[5],'commentPost':result[6],'senderName':result[7],'commentTime':result[8]}
    #    payload.append(content)
    #    content = {}
    for result in twoTable:
       content = {'commentPost':result[6],'senderName':result[7],'commentTime':result[8]}
       payload.append(content)
       content = {}

    connection.close()
    #result = postandcomment_schema.dump(twoTable)
    return jsonify(payload)

@app.route('/yorumlar/<postID>',methods=['GET'])
def get_yorumlar(postID):
    yorumlar = postComment.query.get(postID)
    print(comments_schema.jsonify(yorumlar))
    return comments_schema.jsonify(yorumlar)


@app.route('/posts/<id>', methods=['GET'])
def get_posts_id(id):
    #post = posts.query.get(id)
    post = posts.query.get(id)
    print(posts_schema.jsonify(post))
    return posts_schema.jsonify(post)


@app.route("/posts/<id>", methods=["DELETE"])
def user_delete(id):
    user = posts.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return posts_schema.jsonify(user)


# Run the Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)