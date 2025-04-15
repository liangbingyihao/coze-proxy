from flask import Blueprint
from flasgger import Swagger


def init_api(app):
    # 主蓝图
    main_bp = Blueprint('api', __name__, url_prefix='/api')

    # 注册子蓝图
    from auth import auth_bp
    from user import user_bp
    # from .docs import docs_bp

    main_bp.register_blueprint(auth_bp)
    main_bp.register_blueprint(user_bp)
    # main_bp.register_blueprint(docs_bp)

    # 注册主蓝图
    app.register_blueprint(main_bp)

    # 初始化Swagger
    Swagger(app, template_file='static/swagger.json')