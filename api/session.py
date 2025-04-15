from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.session_schema import SessionSchema
from services.auth_service import AuthService
from schemas.user_schema import AuthSchema, UserSchema
from services.session_service import SessionService
from services.user_service import UserService
from utils.exceptions import AuthError

session_bp = Blueprint('session', __name__)


@session_bp.route('/add', methods=['POST'])
@jwt_required()
def add():
    data = request.get_json()
    session_name = data.get('session_name')
    owner_id = get_jwt_identity()
    robt_id = data.get('robt_id')

    try:
        session = SessionService.new_session(session_name, owner_id, robt_id)
        return jsonify({
            'success': True,
            'data': SessionSchema().dump(session)
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@session_bp.route('/mine', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'my sessions',
    # 类似上面的Swagger定义
})
@jwt_required()
def my_sessions():
    owner_id = get_jwt_identity()

    try:
        data = SessionService.get_session_by_owner(owner_id)
        return jsonify({
            'success': True,
            'data': SessionSchema(many=True).dump(data)
        })
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(str(e), 500)
