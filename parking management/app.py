from flask import Flask
from extensions import db  
from controllers.file_1 import main_routes
from models.model import User_Info  # for admin

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-very-secret-key-here'

    db.init_app(app) 
    app.register_blueprint(main_routes)

    return app

app = create_app()

with app.app_context():
    from models.model import *
    db.create_all()

    # admin
    admin = User_Info.query.filter_by(role=0).first()
    if not admin:
        new_admin = User_Info(
            email='admin@example.com',
            full_name='Super Admin',
            user_name='admin',
            pwd='admin123',
            role=0  # 0 = admin
        )
        db.session.add(new_admin)
        db.session.commit()
        print(" Admin created: admin/admin123")
    else:
        print(" Admin already exists.")

if __name__ == '__main__':
    app.run(debug=True)

