from wtforms import validators, Form, StringField, PasswordField, TextAreaField


class signUpForm(Form):
    userName = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
        render_kw={"placeholder": "شناسه کاربری"},
    )
    email = StringField(
        "Email",
        [validators.Length(min=6, max=50), validators.InputRequired()],
        render_kw={"placeholder": "ایمیل"},
    )
    password = PasswordField(
        "Password",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "رمز عبور"},
    )
    passwordConfirm = PasswordField(
        "passwordConfirm",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "تکرار رمز عبور"},
    )

class loginForm(Form):
    userName = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
        render_kw={"placeholder": "شناسه کاربری"},
    )
    password = PasswordField(
        "Password",
        [validators.Length(min=5), validators.InputRequired()],
        render_kw={"placeholder": "رمز عبور"},
    )

class verifyUserForm(Form):
    code = StringField(
        "code",
        [validators.Length(min=4, max=4), validators.InputRequired()],
        render_kw={"placeholder": "کد اعتبارسنجی"},
    )

class passwordResetForm(Form):
    userName = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
        render_kw={"placeholder": "شناسه کاربری"},
    )
    email = StringField(
        "Email",
        [validators.Length(min=6, max=50), validators.InputRequired()],
        render_kw={"placeholder": "ایمیل"},
    )
    code = StringField(
        "code",
        [validators.Length(min=4, max=4), validators.InputRequired()],
        render_kw={"placeholder": "کد اعتبارسنجی"},
    )
    password = PasswordField(
        "Password",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "رمز عبور"},
    )
    passwordConfirm = PasswordField(
        "passwordConfirm",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "تکرار رمز عبور"},
    )

class changePasswordForm(Form):
    oldPassword = PasswordField(
        "oldPassword",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "رمز عبور قدیمی"},
    )
    password = PasswordField(
        "password",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "رمز عبور جدید"},
    )
    passwordConfirm = PasswordField(
        "passwordConfirm",
        [
            validators.Length(min=8),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "تکرار رمز عبور"},
    )

class changeUserNameForm(Form):
    newUserName = StringField(
        "Username",
        [validators.Length(min=4, max=25), validators.InputRequired()],
        render_kw={"placeholder": "شناسه کاربری جدید"},
    )

class createPostForm(Form):
    postTitle = StringField(
        "Post Title",
        [validators.Length(min=4, max=75), validators.InputRequired()],
        render_kw={"placeholder": "عنوان مطلب"},
    )
    postTags = StringField(
        "Post Tags", [validators.InputRequired()], render_kw={"placeholder": "تگ ها"}
    )
    postContent = TextAreaField(
        "Post Content",
        [validators.Length(min=50)],
    )

class commentForm(Form):
    comment = TextAreaField(
        "Comment",
        [validators.Length(min=20, max=500), validators.InputRequired()],
        render_kw={"placeholder": "کامنت خود را ارسال کنید"},
    )
