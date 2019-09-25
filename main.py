from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogtastic@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    

    def __init__(self, title, body):
        self.title = title
        self.body = body
        
@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)

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

        return render_template('newpost.html',title="Build-a-Blog")

@app.route('/blog', methods=['GET'])
def blog():

    if 'id' in request.args:
        blog_id = int(request.args.get('id'))

        blog = Blog.query.get(blog_id)

        return render_template('singleblog.html', title="Build a Blog", blog=blog)

    else:

        blogs = Blog.query.order_by(Blog.pub_date.desc()).all()

        return render_template('blog.html', title="Build a Blog", blogs=blogs)

if __name__ == '__main__':
    app.run()