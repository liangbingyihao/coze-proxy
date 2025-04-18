from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.message_schema import MessageSchema
from services.message_service import MessageService

message_bp = Blueprint('message', __name__)


@message_bp.route('', methods=['POST'])
@jwt_required()
def add():
    data = request.get_json()
    content = data.get('text')
    owner_id = get_jwt_identity()
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "Missing required parameter 'session_id'"}), 400
    if not content:
        return jsonify({"error": "Missing required parameter 'text'"}), 400

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


@message_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'my sessions',
    # 类似上面的Swagger定义
})
@jwt_required()
def my_message():
    owner_id = get_jwt_identity()
    # 获取特定参数（带默认值）
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    search = request.args.get('search', default='', type=str)
    session_id = request.args.get("session_id", default='', type=str)
    context_id = request.args.get("context_id", default='', type=str)

    try:
        data = MessageService.filter_message(owner_id=owner_id, session_id=session_id, context_id=context_id,
                                             search=search, page=page,
                                             limit=limit)
        import flask_sqlalchemy
        if isinstance(data,flask_sqlalchemy.BaseQuery):
            return jsonify({
                'success': True,
                'data': {
                    'items': MessageSchema(many=True).dump(data)
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'items': MessageSchema(many=True).dump(data.items),
                    'total': data.total
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
