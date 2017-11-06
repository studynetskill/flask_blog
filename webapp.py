# encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session, g
import config
from models import User, Blog, Comment
from exts import db
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    content = {
        'blogs': Blog.query.order_by('-create_time').all()
    }
    return render_template('index.html', **content)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 如果想在31天内都不用登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号码或者密码错误，请检查后在登录！'

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.method == 'GET':
        return render_template('blog.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        blog = Blog(title=title, content=content)
        blog.author = g.user
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<blog_id>')
def detail(blog_id):
    blog_detail = Blog.query.filter(Blog.id == blog_id).first()

    return render_template('detail.html', blog=blog_detail)

@app.route('/addComment/', methods=['POST'])
# @login_required
def addComment():
    content = request.form.get('comment_content')
    blog_id = request.form.get('blog_id')
    comment = Comment(content=content)
    comment.author = g.user
    blog = Blog.query.filter(Blog.id == blog_id).first()
    comment.blog = blog

    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', blog_id=blog_id))

@app.route('/search/')
def search():
    q = request.args.get('q')
    found_blogs = Blog.query.filter(or_(Blog.title.contains(q), Blog.content.contains(q))).order_by('-create_time')
    return render_template('index.html', blogs=found_blogs)


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 手机号码验证，如果已经注册就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号码已经被注册了，请更换手机！'
        else:
            # password1和password2要相等
            if password1 != password2:
                return u'两次密码不相等，请核对后再填写'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功就跳转到登录页面
                return redirect(url_for('login'))

@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user

@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    return {}
if __name__ == '__main__':
    app.run()
