from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask (__name__)
    app.secret_key = 'labambuia' #maybe delete this to uncrypt cookies and stuff
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix ='/')
    app.register_blueprint(auth, url_prefix ='/')

    from .models import User,Note

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Database created!')
        
        admin = User.query.filter_by(email='admin@admin.com').first()
        if not admin:
            admin = User(email='admin@admin.com', first_name='admin', password=generate_password_hash('admin', method='sha256'))
            db.session.add(admin)
            db.session.commit()
            print('ADMIN CREATED')

    @login_manager.user_loader
    def load_user(id):
        if id is not None:
            print(id)
            return User.query.get(int(id)) 

    return app