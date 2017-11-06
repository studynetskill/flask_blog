# conding: utf-8

from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	telephone = db.Column(db.String(11), nullable=False)
	username = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(100), nullable=False)

	def __init__(self, **kwargs):
		self.telephone = kwargs.get('telephone')
		self.username = kwargs.get('username')
		self.password = generate_password_hash(kwargs.get('password'))

	def check_password(self, raw_password):
		# 检查密码
		result = check_password_hash(self.password, raw_password)
		return result

class Blog(db.Model):
	__tablename__ = 'blog'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	title = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	create_time = db.Column(db.DateTime, default=datetime.now)

	author = db.relationship('User', backref=db.backref('blogs'))


class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	content = db.Column(db.Text, nullable=False)
	blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	create_time = db.Column(db.DateTime, default=datetime.now)

	blog = db.relationship('Blog', backref=db.backref('comments', order_by=id.desc()))
	author = db.relationship('User', backref=db.backref('comments'))
