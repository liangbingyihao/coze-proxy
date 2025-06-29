import json
import logging

import click
import pymysql
from flask import Flask
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, migrate
from flask_cors import CORS

from api import init_api
from config import Config
from utils.exceptions import AuthError, handle_auth_error
from extensions import db
from utils.security import generate_password_hash

pymysql.install_as_MySQLdb()


# # 初始化应用
# app = Flask(__name__)
# app.config.from_object(Config)
#
# # 初始化扩展
# db.init_app(app)
# migrate = Migrate(app, db)
# jwt = JWTManager(app)
# CORS(app)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app)

    # 初始化API
    init_api(app)

    # 注册错误处理器
    app.register_error_handler(AuthError, handle_auth_error)
    register_commands(app)

    return app


def register_commands(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        """Initialize the database
        flask init-db
        flask run
        ."""
        db.create_all()

        from services.message_service import MessageService
        MessageService.init_welcome_msg()

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    @with_appcontext
    def create_user(username, email, password):
        """Create a new user."""
        from models.user import User
        from utils.security import generate_password_hash

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        print(f"User {username} created.")


#
# # API路由
# @app.route('/api/auth/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')
#
#     try:
#         user = AuthService.register_user(username, email, password)
#         return jsonify({
#             'success': True,
#             'data': UserSchema().dump(user)
#         }), 201
#     except AuthError as e:
#         raise e
#     except Exception as e:
#         raise AuthError(str(e), 500)
#
#
# @app.route('/api/auth/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#
#     try:
#         auth_data = AuthService.login_user(username, password)
#         return jsonify({
#             'success': True,
#             'data': AuthSchema().dump(auth_data)
#         })
#     except AuthError as e:
#         raise e
#     except Exception as e:
#         raise AuthError(str(e), 500)
#
#
# @app.route('/api/auth/me', methods=['GET'])
# @jwt_required()
# def get_current_user():
#     user_id = get_jwt_identity()
#     user = UserService.get_user_by_id(user_id)
#
#     if not user:
#         raise AuthError('User not found', 404)
#
#     return jsonify({
#         'success': True,
#         'data': UserSchema().dump(user)
#     })


if __name__ == '__main__':
    app = create_app()
    # app.logger.setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
