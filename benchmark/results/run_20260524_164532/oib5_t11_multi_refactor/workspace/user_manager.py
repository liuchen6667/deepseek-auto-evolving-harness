"""用户管理模块"""

import common

DATA_FILE = "users.json"


def load_users():
    return common.load_json(DATA_FILE)


def save_users(users):
    common.save_json(users, DATA_FILE)


def find_user(users, user_id):
    return common.find_by_id(users, user_id)


def validate_email(email):
    return "@" in email and "." in email.split("@")[1]