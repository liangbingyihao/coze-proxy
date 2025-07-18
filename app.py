import json
import logging
import traceback

import click
import pymysql
from flask import Flask, app, request, jsonify
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, migrate
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

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

    # 统一处理400错误
    @app.errorhandler(400)
    def handle_bad_request(error):
        # 获取错误堆栈
        error_stack = traceback.format_exc()

        # 记录业务日志（包含请求信息）
        logger.error(
            f"400 Bad Request\n"
            f"URL: {request.url}\n"
            f"Method: {request.method}\n"
            f"Headers: {dict(request.headers)}\n"
            f"Body: {request.get_data(as_text=True)}\n"
            f"Error: {str(error)}\n"
            f"Stack Trace:\n{error_stack}"
        )

        # 返回标准化错误响应
        return jsonify({
            "status": "error",
            "code": 400,
            "message": str(error),
            "stack_trace": error_stack if app.debug else None  # 调试模式下显示堆栈
        }), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        # 记录错误日志
        logger.error(f"Error occurred: {str(e)}", exc_info=True)

        # 如果是HTTP异常，保留原始状态码和描述
        if isinstance(e, HTTPException):
            return jsonify({
                'success': False,
                'message': e.description
            }), e.code

        # 其他异常统一返回400
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


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
    # app.logger.setLevel(logging.DEBUG)
    app = create_app()
    app.run(host="0.0.0.0", debug=True)
