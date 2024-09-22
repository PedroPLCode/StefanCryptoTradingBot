from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
admin = Admin(template_mode='bootstrap4')
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicjalizuj komponenty
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Ustawienia administracyjne
    from .models import User, Settings, TradeHistory
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Settings, db.session))
    admin.add_view(ModelView(TradeHistory, db.session))

    # Rejestruj blueprint
    from .routes import main
    app.register_blueprint(main)

    # Definiuj user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app