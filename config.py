SECRET_KEY = 'this-is-a-secret-key'
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# database Setting
SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'
# SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/blog'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root@localhost/blog'


# social login Setting
GITHUB_OAUTH_CLIENT_ID = "your-client-id"
GITHUB_OAUTH_CLIENT_SECRET = "your-client-secret"


# Email Service Setting
SITE_USER_URL = "http://127.0.0.1:5000/user/" # for create user qrcode
SMTP_SERVER = "smtp-mail.outlook.com"
SENDER_EMAIL = "email@outlook.com"
PASSWORD_EMAIL = "your-password-outlook"
SMTP_PORT = 587
