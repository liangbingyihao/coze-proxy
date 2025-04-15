from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.user_schema import UserSchema
from services.user_service import UserService
from utils.exceptions import AuthError

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'List of users'},
        401: {'description': 'Unauthorized'}
    }
})
def get_users():
    users = UserService.get_all_users()
    return jsonify({
        'success': True,
        'data': UserSchema(many=True).dump(users)
    })


@user_bp.route('/me', methods=['GET'])
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
