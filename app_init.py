from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config
from .utils.exceptions import AuthError, handle_auth_error
from .services.auth_service import AuthService
from .services.user_service import UserService
from .schemas.user_schema import UserSchema, AuthSchema

# 初始化应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# 注册错误处理器
app.register_error_handler(AuthError, handle_auth_error)

# 导入模型（确保模型被注册）
from .models.user import User


# 初始化数据库
@app.before_first_request
def create_tables():
    db.create_all()


# API路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        user = AuthService.register_user(username, email, password)
        return jsonify({
            'success': True,
            'data': UserSchema().dump(user)
        }), 201
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(str(e), 500)


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        auth_data = AuthService.login_user(username, password)
        return jsonify({
            'success': True,
            'data': AuthSchema().dump(auth_data)
        })
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(str(e), 500)


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = UserService.get_user_by_id(user_id)

    if not user:
        raise AuthError('User not found', 404)

    return jsonify({
        'success': True,
        'data': UserSchema().dump(user)
    })


if __name__ == '__main__':
    app.run(debug=True)