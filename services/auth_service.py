from models.user import User
from utils.security import generate_jwt_token
from utils.exceptions import AuthError


class AuthService:
    @staticmethod
    def register_user(username, email, password):
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise AuthError('Username already exists', 400)

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise AuthError('Email already exists', 400)

        # 创建新用户
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()

        if not user or not user.verify_password(password):
            raise AuthError('Invalid username or password', 401)

        # 生成JWT令牌
        access_token = generate_jwt_token(user.id)

        return {
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }