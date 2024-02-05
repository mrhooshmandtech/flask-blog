from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_dance.contrib.github import make_github_blueprint, github
from werkzeug.utils import secure_filename

from email.message import EmailMessage
import smtplib
import os
import ssl

from random import randint
from jdatetime import datetime

from flask_sqlalchemy import SQLAlchemy
from database import db  

from forms import *
from config import *
from models import * 


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.config["GITHUB_OAUTH_CLIENT_ID"] = GITHUB_OAUTH_CLIENT_ID
app.config["GITHUB_OAUTH_CLIENT_SECRET"] = GITHUB_OAUTH_CLIENT_SECRET


db.init_app(app)


def currentDate():
    return datetime.now().strftime("14%y/%m/%d")

def currentTime(seconds=False):
    if not seconds:
        return datetime.now().strftime("%H:%M")
    else:
        return datetime.now().strftime("%H:%M:%S")

def deleteUser(userName):
    user = User.query.filter_by(userName=userName.lower()).first()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return redirect(f"/admin/users")

def deletePost(postID):
    post = Post.query.get(postID)
    
    if post:
        db.session.delete(post)
        db.session.commit()
        comments = Comment.query.filter_by(post=postID).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()

        return redirect("/")

def deleteComment(commentID):
    comment = Comment.query.get(commentID)

    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash('کامنت  مورد نظر حذف شد', "success")
        return redirect("/")
    else:
        flash('کامنت مورد نظر پیدا نشد!', "error")
        return redirect("/")

def sendEmailSmtp(subject, userName, email):
    context = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(SENDER_EMAIL, PASSWORD_EMAIL,)
    message = EmailMessage()

    code = str(randint(1000, 9999))

    if subject == "verificationCode":
        message.set_content(
            f"سلام {userName} عزیز 🖖\n📌 کد اعتبار سنجی شما : \n{code}"
        )
        message.add_alternative(
            f"""\
        <html>
            <body>
                <h2>سلام {userName}🖖,</h2>
                <h3>📌 کد اعتبار سنجی شما :</h3>
                <h1>{code}</h1>
            </body>
        </html>
        """,
            subtype="html",
        )
        message["Subject"] = "کد اعتبارسنجی"
    
    else:
        
        message.set_content(
            f"سلام {userName}🖖,\nرمز عبور خود را فراموش کرده اید؟ 🤔\nکد تغییر رمز عبور شما :\n{code}"
        )
        message.add_alternative(
            f"""\
        <html>
            <body>
                <h2>سلام {userName}🖖,</h2>
                <h3>رمز عبور خود را فراموش کرده اید؟ 🤔<br>کد تغییر رمز عبور شما :</h3>
                <h1>{code}</h1>
                </body>
        </html>
        """,
            subtype="html",
        )
        message["Subject"] = "فراموشی رمز عبور"

    message["From"] = f"{SENDER_EMAIL}"
    message["To"] = email

    try:
        return "success", code
    except:
        return "error", code

def create_admin_account():
    admin = User.query.filter_by(userName="admin").first()
    if admin:
        return "admin exist!"
    else:
        admin = User(
                userName="admin", 
                email="admin@admin.admin", 
                password=generate_password_hash("admin", method='pbkdf2:sha256'),
                profilePicture= f"https://qr-code.ir/api/qr-code/?d={SITE_USER_URL}admin",
                role="admin",
                creationDate=currentDate(),
                creationTime=currentTime(),
                isVerfied="True"
        )
        db.session.add(admin)
        db.session.commit()
        return "admin created"



github_bp = make_github_blueprint()
app.register_blueprint(github_bp, url_prefix="/login-github")

@app.route("/login-github")
def login_github_acc():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    session["userName"] = resp.json()["login"]
    flash("ورود موفقیت آمیز بود خوشامدید", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    db.create_all()
    create_admin_account()
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    match "userName" in session:
        case True:
            flash("شما قبلا وارد شده اید", "error")
            return redirect("/")
        case False:
            form = signUpForm(request.form)
            
            if request.method == "POST" and form.validate():
                
                username = form.userName.data
                email = form.email.data
                password = form.password.data
                passwordConfirm = form.passwordConfirm.data

                existing_user = User.query.filter_by(userName=username.lower()).first()
                if existing_user:
                    flash("این نام کاربری قبلاً استفاده شده است", "error")
                    return render_template("signup.html", form=form)
                
                existingEmail = User.query.filter_by(email=email).first()
                if existingEmail:
                    return render_template("signup.html", form=form, error="این ایمیل قبلاً استفاده شده است.")
                
                if password != passwordConfirm:
                    flash("رمز عبور و تکرار آن همخوانی ندارند", "error")
                    return render_template("signup.html", form=form)

                if passwordConfirm == password:
                    match username.isascii():
                        case True:
                            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')
                            newUser = User(
                                userName=username.lower(),
                                email=email,
                                password=hashedPassword, 
                                profilePicture= f"https://qr-code.ir/api/qr-code/?d={SITE_USER_URL}{username}",
                                role="user",
                                creationDate=currentDate(),
                                creationTime=currentTime(),
                                isVerfied="False"
                                )
                            db.session.add(newUser)
                            db.session.commit()
                            session["userName"] = username
                            flash(f"ثبت نام با موفقیت انجام شد {username} عزیز خوشامدید:)", "success")
                            return redirect("/verifyUser/codesent=false")
                        case False:
                            flash(f"خوشامدید {username}", "success")
                            flash("شناسه کاربری معتبر نمی باشد","error")
            return render_template("signup.html", form=form, hideSignUp=True)


@app.route('/verifyUser/codesent=<codeSent>', methods=['GET', 'POST'])
def verifyUser(codeSent):
    match "userName" in session:
        case True:
            userName = session["userName"]
            user = User.query.filter_by(userName=userName.lower()).first()
            isVerfied = user.isVerfied
            match isVerfied:
                case "True":
                    return redirect("/")
                case "False":
                    global verificationCode
                    form = verifyUserForm(request.form)
                    match codeSent:
                        case "true":
                            if request.method == "POST":
                                code = request.form["code"]
                                match code == verificationCode:
                                    case True:
                                        user.isVerfied = "True"
                                        db.session.commit()
                                        flash(
                                            "اکانت شما تایید شد",
                                            "success",
                                        )
                                        return redirect("/")
                                    case False:
                                        flash("کد اشتباه است", "error")
                            return render_template("verifyUser.html", form=form, mailSent=True)
                        case "false":
                            if request.method == "POST":
                                user = User.query.filter_by(userName=userName).first()
                                email = user.email
                                res, verificationCode = sendEmailSmtp(subject="verificationCode", userName=userName, email=email)
                                
                                if res == "success":
                                    flash("کد ارسال شد ایمیل خود را چک کنید", "success")
                                    return redirect("/verifyUser/codesent=true")
                                else:
                                    flash("ارسال کد با خطا مواجه شد!", "error")
                                    return redirect("/verifyUser/codesent=false")
                            
                            return render_template("verifyUser.html", form=form, mailSent=False)
        case False:
            return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    match "userName" in session:
        case True:
            flash("شما قبلا وارد شده اید", "error")
            return redirect(url_for('index'))
        case False:
            form = loginForm(request.form)
            if request.method == "POST" and form.validate():
                username = form.userName.data
                password = form.password.data

                user = User.query.filter_by(userName=username.lower()).first()
                if user and check_password_hash(user.password, password):
                    session["userName"] = username.lower()
                    flash("ورود موفقیت آمیز بود خوشامدید", "success")
                    return redirect(url_for('index'))
                else:
                    flash("شناسه کاربری یا رمز عبور نامعتبر است", "error")
                    return render_template("login.html", form=form)
                
            return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    match "userName" in session:
        case True:
            flash("شما از حساب خود خارج شدید", "success")
            session.clear()
            return redirect("/")
        case False:
            flash("شما هنوز وارد اکانت نشدید", "error")
            return redirect(url_for("login"))

    return redirect(url_for('index'))


@app.route('/passwordreset/codesent=<codeSent>', methods=['GET', 'POST'])
def passwordReset(codeSent):
    form = passwordResetForm(request.form)
    global userName
    global passwordResetCode
    match codeSent:
        case "true":
            if request.method == "POST":
                code = request.form["code"]
                password = request.form["password"]
                passwordConfirm = request.form["passwordConfirm"]
                match code == passwordResetCode:
                    case True:
                        user = User.query.filter_by(username=UserName)
                        checkpass = check_password_hash(user.password, password)
                        match checkpass:
                            case True:
                                flash(
                                    "رمز عبور جدید و قدیم نمی تواند یکسان باشد",
                                    "error",
                                )
                            case False:
                                match password == passwordConfirm:
                                    case True:
                                        password = generate_password_hash(password, method='pbkdf2:sha256')
                                        user.password = password
                                        db.session.commit()

                                        flash(
                                            "شما نیاز به ورود با پسورد جدید دارید",
                                            "success",
                                        )
                                        return redirect(url_for('login'))
                                    case False:
                                        flash(
                                            "رمز عبور و تکرار رمز عبور یکسان نیست!",
                                            "error",
                                        )
                    case False:
                        flash("کد اشتباه است", "error")
            return render_template("passwordReset.html", form=form, mailSent=True)
        case "false":
            if request.method == "POST":
                userName = request.form["userName"]
                email = request.form["email"]
                userName = userName.replace(" ", "")          
                user = User.query.filter_by(userName=userName.lower()).first()
                userEmail = User.query.filter_by(email=email).first()

                match not user or not userEmail:
                    case False:
                        res, passwordResetCode = sendEmailSmtp(subject="PasswordReset", userName=userName, email=email)
                        
                        if res == "success":
                            flash("کد ارسال شد ایمیل خود را چک کنید", "success")
                            return redirect("/passwordreset/codesent=true")
                        else:
                            flash("ارسال کد با خطا مواجه شد!", "error")
                            return redirect("/passwordreset/codesent=false")
                    case True:
                        flash("کاربری با این مشخصات پیدا نشد!", "error")
            return render_template("passwordReset.html", form=form, mailSent=False)


@app.route("/user/<userName>")
def user(userName):
    user = User.query.filter_by(userName=userName).first()
    
    if user and user.isVerfied == "True":
        try:
            posts = Post.query.filter_by(author=str(user.userName))
            views = sum(post.views for post in posts)
        except:
            posts = False
            views = 0
        
        try:
            comments = Comment.query.filter_by(user=user.userName)
        except:
            comments = False

        return render_template(
            "user.html",
            user=user,
            views=views,
            posts=posts,
            comments=comments
        )

    elif user and user.isVerfied == "False":
        flash("اکانت شما تایید نشده است لطفا ابتدا آن را تایید کنید", "error")
        return redirect("/verifyUser/codesent=false")
    
    else:
        return render_template("404.html")


@app.route("/accountsettings", methods=["GET", "POST"])
def accountSettings():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            if request.method == "POST":
                if "userDeleteButton" in request.form:
                    deleteUser(user.userName)
                    flash('اکانت شما حذف شد به امید دیدار مجدد', 'success')
                    return redirect("/")
            return render_template("accountSettings.html", user=user)
        case False:
            return redirect(url_for("login"))


@app.route("/changepassword", methods=["GET", "POST"])
def changePassword():
    match "userName" in session:
        case True:
            form = changePasswordForm(request.form)
            if request.method == "POST":
                oldPassword = request.form["oldPassword"]
                password = request.form["password"]
                passwordConfirm = request.form["passwordConfirm"]
                user = User.query.filter_by(userName=session["userName"]).first()
                
                if check_password_hash(user.password, oldPassword):
                    if oldPassword == password:
                        flash("پسورد جدید نمی تواند با پسورد قبلی یکی باشد", "error")
                    elif password != passwordConfirm:
                        flash("رمز عبور و تکرار رمز عبور یکی نیست!", "error")
                    elif oldPassword != password and password == passwordConfirm:
                        newPassword = generate_password_hash(password, method='pbkdf2:sha256')
                        user.password = newPassword
                        db.session.commit()
                        session.clear()
                        flash("شما نیازمند ورود مجدد هستید", "success")
                        return redirect(url_for("login"))
                else:
                    flash("پسورد قبلی اشتباه است", "error")

            return render_template("changePassword.html", form=form)
        case False:
            flash("برای تغییر پسورد نیاز به ورود دارید", "error")
            return redirect(url_for("login"))


@app.route("/changeusername", methods=["GET", "POST"])
def changeUserName():
    match "userName" in session:
        case True:
            form = changeUserNameForm(request.form)
            if request.method == "POST":
                newUserName = request.form["newUserName"]
                newUserName = newUserName.replace(" ", "")

                newUser = User.query.filter_by(userName=newUserName).first()
                
                match newUserName.isascii():
                    case True:
                        match newUserName == session["userName"]:
                            case True:
                                flash("شناسه فعلی شما همین شناسه می باشد", "error")
                            case False:
                                match newUser == None:
                                    case True:
                                        user = User.query.filter_by(userName=session["userName"]).first()
                                        user.userName = newUserName
                                        user.profilePicture = f"https://qr-code.ir/api/qr-code/?d={SITE_USER_URL}{newUserName}"
                                        db.session.commit()
                                        
                                        try:
                                            posts = Post.query.filter_by(author=session["userName"]).first()
                                            for post in posts:
                                                post.author.userName = newUserName
                                            db.session.commit()
                                        except:
                                            pass
                                        try:
                                            comment = Comment.query.filter_by(author=session["userName"]).first()
                                            for comment in comments:
                                                comment.author.userName = newUserName
                                            db.session.commit()
                                        except:
                                            pass

                                        session["userName"] = newUserName
                                        flash("شناسه شما با موفقیت تغییر یافت", "success")
                                        return redirect(f"/user/{newUserName.lower()}")
                                    case False:
                                        flash(
                                            "شناسه ای که وارد کرده اید از قبل موجود است", "error"
                                        )
                    case False:
                        flash("لطفا یک شناسه معتبر شامل حروف و اعداد وارد کنید", "error")

            return render_template("changeUserName.html", form=form)
        case False:
            return redirect("/")


@app.route("/dashboard/<userName>", methods=["GET", "POST"])
def dashboard(userName):
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            if user.isVerfied == "False":
                    flash("اکانت شما تایید نشده است لطفا ابتدا آن را تایید کنید", "error")
                    return redirect("/verifyUser/codesent=false")
            
            match session["userName"].lower() == userName.lower():
                case True:
                    if request.method == "POST":
                        if "postDeleteButton" in request.form:
                            postID = request.form["postID"]
                            deletePost(postID)
                            return redirect(f"/dashboard/{userName}")
                    
                    try:
                        posts = Post.query.filter_by(author=session["userName"]).all()
                        showPosts = True
                    except:
                        showPosts = False
                        posts = None
                    try:
                        comments = Comment.query.filter_by(user=session["userName"]).all()
                        showComments = True
                    except:
                        showComments = False
                        comments = None
                    
                    return render_template(
                        "dashboard.html",
                        posts=posts,
                        comments=comments,
                        showPosts=showPosts,
                        showComments=showComments,
                    )
                case False:
                    flash("پنل کاربری برای این کاربر وجود ندارد", "error")
                    return redirect(f'/dashboard/{session["userName"].lower()}')
        case False:
            flash("برای دسترسی به پنل کاربری نیاز به ورود به اکانت دارید", "error")
            return redirect(url_for("login"))


@app.route("/createpost", methods=["GET", "POST"])
def createPost():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            if user.isVerfied == "False":
                    flash("اکانت شما تایید نشده است لطفا ابتدا آن را تایید کنید", "error")
                    return redirect("/verifyUser/codesent=false")
            form = createPostForm(request.form)
            if request.method == "POST":
                postTitle = request.form["postTitle"]
                postTags = request.form["postTags"]
                postContent = request.form["postContent"]
                match postContent == "":
                    case True:
                        flash("محتوای مطلب نمی تواند خالی باشد", "error")
                    case False:
                        newPost = Post(
                            title = postTitle,
                            tags = postTags,
                            content = postContent,
                            author = session["userName"],
                            date = currentDate(),
                            time = currentTime(),
                            views = 0,
                            lastEditDate = currentDate(),
                            lastEditTime = currentTime()
                        )
                        db.session.add(newPost)
                        db.session.commit()
                        flash("مطلب شما اضافه شد", "success")
                        return redirect("/")
            
            return render_template("createPost.html", form=form)
        case False:
            flash("برای اضافه کردن مطلب ابتدا وارد اکانت خود شوید", "error")
            return redirect(url_for("login"))


@app.route("/editpost/<int:postID>", methods=["GET", "POST"])
def editPost(postID):
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            if user.isVerfied == "False":
                    flash("اکانت شما تایید نشده است لطفا ابتدا آن را تایید کنید", "error")
                    return redirect("/verifyUser/codesent=false")
            post = Post.query.get(postID)
            posts = Post.query.all()
            match post in posts:
                case True:
                    authorPost = post.author
                    match authorPost == session["userName"]:
                        case True:
                            form = createPostForm(request.form)
                            form.postTitle.data = post.title
                            form.postTags.data = post.tags
                            form.postContent.data = post.content
                            if request.method == "POST":
                                postTitle = request.form["postTitle"]
                                postTags = request.form["postTags"]
                                postContent = request.form["postContent"]
                                match postContent == "":
                                    case True:
                                        flash("محتوای مطلب نمی تواند خالی باشد!", "error")
                                    case False:
                                        post.title = postTitle
                                        post.tags = postTags
                                        post.content = postContent
                                        post.lastEditDate = currentDate()
                                        post.lastEditTime = currentTime()
                                        db.session.commit()
                                        flash("مطلب شما ویرایش شد", "success")
                                        return redirect(f"/post/{post.id}")
                            return render_template(
                                "editPost.html",
                                title=post.title,
                                tags=post.tags,
                                content=post.content,
                                form=form,
                            )
                        case False:
                            flash("نویسنده این مطلب شما نیستید!", "error")
                            return redirect("/")
                case False:
                    return render_template("404.html")
        case False:
            flash("برای ویرایش مطلب ابتدا وارد اکانت شوید", "error")
            return redirect(url_for("login"))


@app.route("/post/<int:postID>", methods=["GET", "POST"])
def post(postID):
    form = commentForm(request.form)
    post = Post.query.get(postID)
    posts = Post.query.all()
    match post in posts:
        case True:
            post.views +=1
            db.session.commit()
            if request.method == "POST":
                if "postDeleteButton" in request.form:
                    deletePost(postID)
                    return redirect(f"/")
                elif "commentDeleteButton" in request.form:
                    deleteComment(request.form["commentID"])
                    return redirect(f"/post/{postID}")
                else:
                    comment = request.form["comment"]
                    newComment = Comment(
                        post=post.id,
                        comment=comment,
                        user = session["userName"],
                        date = currentDate(),
                        time = currentTime()
                    )
                    db.session.add(newComment)
                    db.session.commit()
                    flash("کامنت شما ثبت شد", "success")
                    return redirect(f"/post/{postID}")
            try:
                comments = Comment.query.filter_by(post=post.id)
            except:
                comments = False
            
            user = User.query.filter_by(userName=post.author).first()
            profilePicture = user.profilePicture
            return render_template(
                "post.html",
                post=post,
                form=form,
                profilePicture=profilePicture,
                comments=comments,
            )
        case False:
            return render_template("404.html")


@app.route("/searchbar")
def searchBar():
    return render_template("searchBar.html")


@app.route("/search/<query>", methods=["GET", "POST"])
def search(query):
    try:
        posts = Post.query.filter(Post.title.like(f"%{query}%")).all()
    except:
        posts = None
    
    return render_template(
        "search.html",
        posts=posts,
        query=query
    )


@app.route("/admin")
def adminPanel():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            match "admin" in user.role:
                case True:
                    return render_template("adminPanel.html")
                case False:
                    return redirect("/")
        case False:
            return redirect("/")


@app.route("/admin/posts", methods=["GET", "POST"])
@app.route("/adminpanel/posts", methods=["GET", "POST"])
def adminPanelPosts():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            match "admin" in user.role:
                case True:
                    if request.method == "POST":
                        if "postDeleteButton" in request.form:
                            deletePost(request.form["postID"])
                    posts = Post.query.all()
                    return render_template("dashboard.html", posts=posts, showPosts=True)
                case False:
                    return redirect("/")
        case False:
            return redirect("/")


@app.route("/admin/users", methods=["GET", "POST"])
@app.route("/adminpanel/users", methods=["GET", "POST"])
def adminPanelUsers():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            match "admin" in user.role:
                case True:
                    if request.method == "POST":
                        if "userDeleteButton" in request.form:
                            deleteUser(request.form["userName"])
                    users = User.query.all()
                    return render_template(
                        "adminPanelUsers.html",
                        users=users,
                    )
                case False:
                    return redirect("/")
        case False:
            return redirect("/")


@app.route("/admin/comments", methods=["GET", "POST"])
@app.route("/adminpanel/comments", methods=["GET", "POST"])
def adminPanelComments():
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            match "admin" in user.role:
                case True:
                    if request.method == "POST":
                        if "commentDeleteButton" in request.form:
                            deleteComment(request.form["commentID"])
                            return redirect(f"/admin/comments")
                    comments = Comment.query.all()
                    return render_template("adminPanelComments.html", comments=comments)
                case False:
                    return redirect("/")
        case False:
            return redirect("/")

@app.route("/setuserrole/<userName>/<newRole>")
def setUserRole(userName, newRole):
    match "userName" in session:
        case True:
            user = User.query.filter_by(userName=session["userName"]).first()
            match "admin" in user.role :
                case True:
                    user.role = f"{newRole}"
                    db.session.commit()
                    flash(f"کاربر به نقش {newRole} تغییر سمت داد!", "success")
                    return redirect("/admin/users")
                case False:
                    return redirect("/")
        case False:
            return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
