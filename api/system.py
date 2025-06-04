from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity

from schemas.user_schema import UserSchema
from services.coze_service import  msg_feedback,msg_explore,msg_pray
from services.message_service import MessageService
from services.user_service import UserService
from utils.exceptions import AuthError

system_bp = Blueprint('system', __name__)


@system_bp.route('/conf', methods=['GET'])
@jwt_required()
def get_configure():
    return jsonify({
        'success': True,
        'data': {"prompt":msg_feedback,
                 "prompt"+MessageService.action_daily_talk:msg_explore,
                 "prompt"+MessageService.action_daily_pray:msg_pray}
    })

