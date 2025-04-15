import base64
from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return {"error": "Authentication required"}, 401

        try:
            creds = base64.b64decode(auth[6:]).decode('utf-8')
            username, password = creds.split(':', 1)
            # 这里应该验证用户名密码
            if username != 'admin' or password != 'secret':
                return {"error": "Invalid credentials"}, 401
        except:
            return {"error": "Invalid auth header"}, 400

        return f(*args, **kwargs)

    return decorated


@app.route('/api/login', methods=['POST'])
def login():
    # 获取 JSON 数据
    user_name = request.args.get('user_name')
    return jsonify({"data": {
        'access_token': "access_token",
        'user_id': user_name,
        'username': user_name,
    }})


@app.route('/api/chat', methods=['POST'])
def chat():
    # 获取 JSON 数据
    data = request.get_json()  # 自动解析请求体中的 JSON
    print(data)
    return jsonify({"result": True})


@app.route('/api/chat', methods=['GET'])
def get_chat():
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify({"error": "No chat_id provided"}), 400
    return jsonify({"message": "test" + chat_id})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
