from flask import Blueprint, request, jsonify
from .models import User
from . import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"msg": "Username or email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity={'id': user.id, 'username': user.username})
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_identity = get_jwt_identity()
    user = User.query.get(current_user_identity['id'])
    return jsonify(user.to_dict()), 200