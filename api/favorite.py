from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.session_schema import SessionSchema
from services.favorite_service import FavoriteService
from services.session_service import SessionService
from utils.exceptions import AuthError

favorite_bp = Blueprint('favorite', __name__)


@favorite_bp.route('', methods=['POST'])
@swag_from({
    'tags': ['Favorites'],
    'parameters': [
        {
            'message_id': '信息id',
            'content_type': '1:收藏用户信息，2：收藏AI信息'
        }
    ],
    'responses': {
        200: {'success': "true/false"}
    }
})
@jwt_required()
def add():
    data = request.get_json()
    message_id = data.get('message_id')
    content_type = data.get('content_type')
    owner_id = get_jwt_identity()

    try:
        res = FavoriteService.new_favorite(owner_id, message_id, content_type)
        return jsonify({
            'success': res
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@favorite_bp.route('/rm', methods=['POST'])
@jwt_required()
def remove():
    data = request.get_json()
    message_id = data.get('message_id')
    content_type = data.get('content_type')
    owner_id = get_jwt_identity()

    try:
        res = FavoriteService.delete_favorite(owner_id, message_id, content_type)
        return jsonify({
            'success': True,
            'data': res
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@favorite_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'my sessions',
    # 类似上面的Swagger定义
})
@jwt_required()
def my_sessions():
    owner_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)

    try:
        data = SessionService.get_session_by_owner(owner_id,page=page,
                                             limit=limit)
        return jsonify({
            'success': True,
            # 'data': SessionSchema(many=True).dump(data),
            'data': {
                'items': SessionSchema(many=True).dump(data.items),
                'total': data.total
            }
        })
    except AuthError as e:
        raise e
    except Exception as e:
        raise AuthError(str(e), 500)
