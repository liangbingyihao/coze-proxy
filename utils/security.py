import bcrypt
from flask import current_app

def generate_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt_token(identity):
    from flask_jwt_extended import create_access_token
    return create_access_token(identity=identity)

def verify_jwt_token(token):
    from flask_jwt_extended import decode_token
    try:
        decoded_token = decode_token(token)
        return decoded_token['sub']
    except:
        return None