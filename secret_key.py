import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=64):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def ensure_secret_key():
    env_file = Path('.env')
    if not env_file.exists():
        secret = generate_secret_key()
        with open('.env', 'w') as f:
            f.write(f'SECRET_KEY={secret}\n')
        return secret

    with open('.env') as f:
        for line in f:
            if line.startswith('SECRET_KEY='):
                return line.strip().split('=')[1]

    # 如果.env存在但没有SECRET_KEY
    secret = generate_secret_key()
    with open('.env', 'a') as f:
        f.write(f'\nSECRET_KEY={secret}\n')
    return secret


print(generate_secret_key())