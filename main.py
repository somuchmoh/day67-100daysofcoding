import datetime
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, url
from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class BlogForm(FlaskForm):
    title = StringField("Blog Title", validators=[DataRequired()])
    subtitle = StringField("Blog Subtitle", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[url()])
    body = CKEditorField("Blog Content")
    submit = SubmitField("Add Post")


@app.route('/', methods=['GET'])
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/blog/<post_id>', methods=['GET'])
def show_post(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalars().all()
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = result[0]
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new-blog', methods=['GET', 'POST'])
def new_blog():
    form = BlogForm()
    date = datetime.datetime.now()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.data["title"],
            subtitle=form.data["subtitle"],
            img_url=form.data["img_url"],
            author=form.data["author"],
            body=form.body.data,
            date=date.strftime("%B %d, %Y"))
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form)


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<post_id>', methods=['GET', 'POST'])
def edit_blog(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalars().all()
    post = result[0]
    form = BlogForm(title=post.title,
                    subtitle=post.subtitle,
                    img_url=post.img_url,
                    author=post.author,
                    body=post.body)
    if form.validate_on_submit():
        post.title = form.data["title"]
        post.subtitle = form.data["subtitle"]
        post.img_url = form.data["img_url"]
        post.author = form.data["author"]
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template("make-post.html", form=form)


# TODO: delete_post() to remove a blog post from the database
@app.route('/delete-post/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalars().all()[0]
    db.session.delete(result)
    db.session.commit()
    redirect(url_for("get_all_posts"))
    return redirect(url_for('get_all_posts'))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
