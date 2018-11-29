import re

from flask_pymongo import PyMongo
from flask import Flask, jsonify, abort, request, render_template, url_for, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
import pymysql
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context as pwd_context

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/first_flask"
app.config['SQLCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'iii'
db = SQLAlchemy(app)
# MongoDb连接配置
# app.config['MONGO_DBNAME'] = 'user1'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/user1'
# app.url_map.strict_slashes = False
# mongo = PyMongo(app)

# limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["100/day, 2/minute, 1/second"])
#MongoDb 查询方法  增add 删 delete 改 update 同理
# @app.route('/find/<username>')
# def find(username):
#     user = mongo.db.user1
#     username1 = user.find_one({"username":username})
#     if username:
#         return "你查找的用户名：" + username1["username"] + " 密码是：" + username1["password"]
#     else:
#         return "你查找的用户并不存在!"

# @limiter.request_filter
# def filter_func():
#     path_url = request.path
#     white_list = ['/exempt']
#     if path_url in white_list:
#         return True
#     else:
#         return False


class Comment(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True,index = True)
    password = db.Column(db.String(128), unique=True)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

def generate_token(users):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': users.id}).decode('ascii')
    return token, expiration



comments = db.session.query(Comment).all()
result = []
for comment in comments:
    result.append(comment.to_json())



# GET表查询
@app.route('/comments/<username>', methods=['GET'])
def comments(username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    return jsonify(result,{'accesstoken':token}),200


# 精准查询1
@app.route('/comments/1/<username>', methods=['GET'])
def comments1(username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    return jsonify(result[0],{'accesstoken':token}), 200


# 精准查询2
@app.route('/comments/2/<username>', methods=['GET'])
def comments2(username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    return jsonify(result[1],{'accesstoken':token}), 200


# 添加数据3
@app.route('/comments/3/<username>', methods=['POST'])
def comments3(username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    if not request.get_json(force=True):
        return "错误"  # 返回404错误
    else:
        commentpost = {
            'id': request.json['id'],  # 取末尾tasks的id号+1
            'username': request.json['username'],  # title必须设置，不能为空。
            'password': request.json.get('password', "")
        }
    result.append(commentpost)
    return jsonify(result,{'accesstoken':token}), 200


# 指定删除4
@app.route('/comments/4/<int:d_id>/<username>', methods=['DELETE'])
def delete_task(d_id,username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    d_comment = result[d_id]
    result.remove(d_comment)
    return jsonify(result,{'accesstoken':token}), 200


# 指定修改5
@app.route('/comments/5/<int:up_id>/<username>', methods=['PUT'])
def update_task(up_id,username):
    user = Comment.query.filter_by(username=username).first()
    token = generate_token(user)
    up_comment = result[up_id]
    up_comment['id'] = request.json.get('id')
    up_comment['username'] = request.json.get('username')
    up_comment['password'] = request.json.get('password')
    return jsonify(result,{'accesstoken':token}), 200


@app.route('/myapp')
def hello_world():
    return "Well done"


if __name__ == '__main__':
    app.run(port = 8080)
