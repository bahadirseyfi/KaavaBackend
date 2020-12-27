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

    #postR = db.relationship('postComment', backref='postComment.postID', primaryjoin='posts.id==postComments.postID', lazy='joined')

    def __init__(self, name, postName, postDescription, postLike):
        self.name = name
        self.postName = postName
        self.postDescription = postDescription
        self.postLike = postLike

class postComment(db.Model):
    __tablename__ = "postComment"
    id = db.Column(db.Integer, primary_key=True)
    postID = db.Column(db.Integer)
    senderName = db.Column(db.String(20))
    commentPost = db.Column(db.String(300))

    #userR = db.relationship('posts', foreign_keys='posts.id')
    #post = db.relationship("posts", backref="postComment")

    def __init__(self, postID, senderName, commentPost):
        self.postID = postID
        self.senderName = senderName
        self.commentPost = commentPost

#posts Schema
class PostsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'postName', 'postDescription', 'postLike')

class CommentsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'postID', 'senderName', 'commentPost')

#Init Schema
posts_schema = PostsSchema()
posts_schema2 = PostsSchema(many=True)

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

    db.session.add(new_posts)
    db.session.commit()

    return posts_schema.jsonify(new_posts)

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
    return jsonify(result)
@app.route('/postComments/<id>',methods=['GET'])
def get_comment_post(id):
    connection = sqlite3.connect('db.sqlite')
    cur = connection.cursor()
    comment_id = postComment.query.get(id)
    twoTable = cur.execute("""SELECT posts.id, posts.name, posts.postDescription, posts.postLike, posts.postTime, postComment.commentPost, postComment.senderName, commentTime FROM posts inner join postComment WHERE postComment.postID = posts.id AND posts.id = ?""",(id))
    twoTable = twoTable.fetchall()
    connection.close()
    return jsonify(twoTable)

@app.route('/posts/<id>', methods=['GET'])
def get_posts_id(id):

    #post = posts.query.get(id)
    comments = postComment.query.get(id)

    # I want to do this -> comments_schema + posts_schema . jsonify(post,comments)
    #HOW CAN I DO
    return comments_schema.jsonify(comments)


@app.route("/posts/<id>", methods=["DELETE"])
def user_delete(id):
    user = posts.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return posts_schema.jsonify(user)


# Run the Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)