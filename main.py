from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogtastic@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'z788Kf@d9Pas!q'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index2']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')
        
@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if 'email' not in session:
        return redirect('/login')

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body, owner)

        title_error = ""
        body_error = ""

        if blog_title == "":
            title_error="Please fill in the title."

        if blog_body == "":
            body_error="Please fill in the body."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()

            blog_id = new_blog.id
            return redirect('/blog?id={0}'.format(blog_id))
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, 
            title_error=title_error, body_error=body_error)
    else:

        return render_template('newpost.html',title="Blogz")

@app.route('/blog', methods=['GET'])
def blog():

    if 'id' in request.args:
        blog_id = int(request.args.get('id'))

        blog = Blog.query.get(blog_id)

        return render_template('singleblog.html', title="Blogz", blog=blog)

    elif 'user' in request.args:
        user_id = int(request.args.get('user'))

        blogs = Blog.query.filter_by(owner_id=user_id).order_by(Blog.pub_date.desc()).all()

        return render_template('singleuser.html', title="Blogz", blogs=blogs)

    else:

        blogs = Blog.query.order_by(Blog.pub_date.desc()).all()

        return render_template('blog.html', title="Blogz", blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    email=""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        error=False
        if not user:
            error=True
            flash('User does not exist.', 'error')
            pass
        elif check_pw_hash(password, user.pw_hash)==False:
            error=True
            flash('User password incorrect.', 'error')
        if error==False:
            session['email'] = email
            flash("Logged in", "success")
            return redirect('/newpost')
    
    return render_template('login.html', email=email)


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    email = ""

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        error=False

        if password != verify:
            flash("Passwords must match.", "error")
            error=True

        if ' ' in password or len(password) < 3:
            flash("Password is not valid.", "error")
            error=True

        if password == "" or verify == "":
            flash("Password cannot be blank.", "error")
            error=True

        if " " in email or "@" not in email or "." not in email or len(email) < 3:
            flash("Email is not valid.", "error")
            error=True

        if email == "":
            flash("Email cannot be blank.", "error")
            error=True

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists.", "error")
            error=True
        
        if error==False:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')
                 
    return render_template('signup.html', email=email)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index2():

    users = User.query.all()

    return render_template('index.html', title="Blogz", users=users)


if __name__ == '__main__':
    app.run()