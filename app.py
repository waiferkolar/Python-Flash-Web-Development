from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_login import login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './static/imgs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.secret_key = "asdfasdfasdf"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def home():
    return render_template("index.html", posts=Post.query.all())

@app.route("/post/detail/<pk>")
def detailPost(pk):
    post = Post.query.get(pk)
    return render_template("post/detail.html",post=post)

@app.route("/member")
def member():
    if session['username'] != None :
        return render_template("member.html", posts=Post.query.all())
    else : 
        return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        re_name = request.form["name"]
        re_email = request.form["email"]
        re_password = request.form["password"]
        en_password = bcrypt.generate_password_hash(re_password)

        try:
            new_user = User(username=re_name, email=re_email,
                            password=en_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect("/")

        except:
            return f"New User insert error {re_name}"

    else:
        return render_template("register.html")


@app.route("/post/create", methods=["POST", "GET"])
def createPost():
    if session['username'] != None:
        if request.method == "POST":
            p_title = request.form["title"]
            p_author = request.form["author"]
            p_content = request.form["content"]
            file = request.files["file"]

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_post = Post(title=p_title, author=p_author,
                                content=p_content, image=file.filename)
                db.session.add(new_post)
                db.session.commit()
                return redirect("/")
            else:
                return "File upload Error!"
        else:
            if session["username"] == "":
                return redirect("/login")
            else:
                return render_template("post/create.html")
    else:
        return redirect("/login")


@app.route("/post/edit/<id>", methods=["POST", "GET"])
def editPost(id):
    if request.method == "POST":

        post = Post.query.get(id)

        post.title = request.form["title"]
        post.author = request.form["author"]
        post.content = request.form["content"]
        filename = request.form["old_image"]
        file = request.files["file"]

        if file:
            filename = file.filename
            sf = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], sf))

        post.image = filename
        db.session.commit()
        return redirect('/member')

    else:
        post = Post.query.get(id)
        return render_template('post/edit.html', post=post)


@app.route("/post/delete/<pk>")
def deletePost(pk):
    post = Post.query.get(pk)
    db.session.delete(post)
    db.session.commit()
    return redirect("/member")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        lo_email = request.form["email"]
        lo_password = request.form["password"]

        login_user = User.query.filter_by(email=lo_email).first()
        if bcrypt.check_password_hash(login_user.password, lo_password):
            session["username"] = login_user.username
            session["email"] = login_user.email
            flash("Welcome Back!")
            return redirect("/member")
        else:
            return "Something is not right"

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["username"] = None
    session["email"] = None
    return redirect("/login")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=True)
