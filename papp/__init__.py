import oauthlib.oauth2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

GOOGLE_CLIENT_ID = '79137493736-uegdgf344gapgr3vnq8b5i8l7dlp5q8s.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '3AKNLXJO86yPQsx1ONOiT0EI'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = oauthlib.oauth2.WebApplicationClient(GOOGLE_CLIENT_ID)

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'thisismysecretkeydonotstealit'
    con_str = 'mssql+pyodbc://sa:Pa$$w0rd@localhost:1401/PythonCheckerDB?driver=ODBC+Driver+17+for+SQL+Server'
    app.config['SQLALCHEMY_DATABASE_URI'] = con_str

    # -- google consts -- #

    # -- end google consts -- #

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    # OAuth 2 client setup

    from .models import UserInfo

    @login_manager.user_loader
    def load_user(username):
        return UserInfo.query.get(username)

    from .auth import auth as auth_blueprint
    from .tasks import tasks as tasks_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(tasks_blueprint)

    return app
