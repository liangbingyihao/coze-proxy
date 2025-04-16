from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.session_schema import SessionSchema
from services.auth_service import AuthService
from schemas.user_schema import AuthSchema, UserSchema
from services.message_service import MessageService
from services.session_service import SessionService
from services.user_service import UserService
from utils.exceptions import AuthError

message_bp = Blueprint('message', __name__)


@message_bp.route('/add', methods=['POST'])
@jwt_required()
def add():
    data = request.get_json()
    content = data.get('content')
    owner_id = get_jwt_identity()
    session_id = data.get("session_id")

    try:
        message_id = MessageService.new_message(session_id, owner_id, content, 0)
        return jsonify({
            'success': True,
            'data': {"id": message_id}
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@message_bp.route('/filter', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'my sessions',
    # 类似上面的Swagger定义
})
@jwt_required()
def my_message():
    owner_id = get_jwt_identity()

    # 转为普通字典
    args_dict = request.args.to_dict()
    # 获取特定参数（带默认值）
    page = args_dict.get('page', '1')
    limit = args_dict.get('limit', '10')
    session_id = args_dict.get("session_id")
    search = request.args.get('search', default='', type=str)

    try:
        data = MessageService.filter_message(owner_id=owner_id, session_id=session_id, search=search, page=page,
                                             limit=limit)
        return jsonify({
            'success': True,
            'data': {
                'data': [msg.to_dict() for msg in data.items],
                'total': data.total
            }
        })
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(str(e), 500)
