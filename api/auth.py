from flask import Blueprint, jsonify, request
from flasgger import swag_from
from services.auth_service import AuthService
from schemas.user_schema import AuthSchema
from utils.exceptions import AuthError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'User registered successfully'},
        400: {'description': 'Invalid input'}
    }
})
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        user = AuthService.register_user(username, email, password)
        return jsonify({
            'success': True,
            'data': AuthSchema().dump(user)
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Login with username and password',
    # 类似上面的Swagger定义
})
def login():
    # 登录实现
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
