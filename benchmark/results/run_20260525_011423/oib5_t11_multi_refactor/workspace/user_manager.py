"""用户管理模块"""

import json
from common import load_json, save_json, find_by_id

DATA_FILE = "users.json"


def load_users():
    return load_json(DATA_FILE)


def save_users(users):
    save_json(users, DATA_FILE)


def find_user(users, user_id):
    return find_by_id(users, user_id)


def validate_email(email):
    return "@" in email and "." in email.split("@")[1]
