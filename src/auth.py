import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_200_OK, HTTP_401_UNAUTHORIZED
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth.post("/register")
def register():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"message": "Please enter a valid email"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).count() > 0:
        return jsonify({"message": "Email already registered"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).count() > 0:
        return jsonify({"message": "Username already registered"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)
    user = User(username=username, email=email, password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user": user.to_dict()}), HTTP_200_OK

@auth.post("/login")
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.password, password):
                # access_token = jwt.encode()
            refresh_token = create_refresh_token(identity=str(user.id)) # JWT subject claim requires a string
            access_token = create_access_token(identity=str(user.id))

            return jsonify({"user": user.to_dict(), "access_token": access_token, "refresh_token": refresh_token}), HTTP_200_OK

    return jsonify({"message": "Wrong credentials"}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({"user": user.to_dict()}), HTTP_200_OK

@auth.get("token/refresh")
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    access_token = create_access_token(identity=user_id)
    return jsonify({"user": user.to_dict(), "access_token": access_token}), HTTP_200_OK