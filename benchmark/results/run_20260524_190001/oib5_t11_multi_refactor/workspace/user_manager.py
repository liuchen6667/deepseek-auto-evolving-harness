"""用户管理模块"""

from common import load_json, save_json, find_by_id

DATA_FILE = "users.json"


def load_users():
    """加载用户数据"""
    return load_json(DATA_FILE)


def save_users(users):
    """保存用户数据"""
    save_json(users, DATA_FILE)


def find_user(users, user_id):
    """根据ID查找用户"""
    return find_by_id(users, user_id, "id")


def validate_email(email):
    return "@" in email and "." in email.split("@")[1]
