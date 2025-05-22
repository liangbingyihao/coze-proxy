import json

import click
import pymysql
from flask import Flask
from flask.cli import with_appcontext
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, migrate
from flask_cors import CORS

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

        from models.message import Message
        if not Message.query.filter_by(owner_id=0).first():
            message = Message(
                session_id=0, owner_id=0, content="", context_id=0, status=0, action=0
            )
            message.feedback_text = '''✨嗨，你好🙌欢迎来到恩语~！
我可以为你记录你的每一件感恩小事💝、圣灵感动🔥、真实感受，甚至讲道亮光🌟哦，
帮助你在信仰路上，不断看到上帝的恩典🌈！
📝文字或🎤语音转文字，就能快速记录，我们会帮你整理⏳~
每天的记录都是我们跟神互动的印记💌，
坚持记录，你很快会发现，上帝如何奇妙地与我们同行👣哦！
快来开始记录吧~🎉  
'''
            message.feedback = json.dumps(
                {"explore": [["我想看包含了今天的经文推荐，实际应用，以及今天大事的“每日恩语”", 1],
                             ["我想看今天的鼓励经文推荐图", 2],
                             ["我记录当下心情或事件后，你会如何帮我整理", 3, '''假设你语音转文字输入心情：在最近的生活变动和迷茫中，虽然暂时看不到方向，甚至对神的安排产生疑问，但最终选择信靠祂的应许——祂深知你的需要，且预备的恩典远超你的期待。
我们已经把你的内容记录到【信心功课】，希望这段经文可以鼓励到你：
“神为爱他的人所预备的，是眼睛未曾看见，耳朵未曾听见，人心也未曾想到的。”（哥林多前书2:9）
信心的功课不容易，神的预备是每日的功课，不需看清全程，只需信靠每一步。
我们可以通过以下几点进行操练：
 1交托祷告 ：写下困惑，向神坦白：“我相信你的预备超乎所想，但求你给我信心。
 2对抗埋怨 ：当怀疑时，默想这节经文并回顾神过去的信实。
 3积极等候 ：专注当下责任（如工作、服侍），像约瑟在监狱中仍尽忠。
 4开阔信心 ：设想神可能带领的多种方式，祷告求祂显明，不局限自己的期待。
 5寻求支持 ：与属灵同伴分享经文，请他们为你守望。''']]}, ensure_ascii=False)
            db.session.add(message)
            db.session.commit()
            print("Initialized the database with welcome msg.")

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
    app = create_app()
    # app.logger.setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)
