from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import Bookmark, db
from src.constants.http_status_codes import HTTP_200_OK

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")

@bookmarks.post("/")
@jwt_required()
def create_bookmark():
    user_id = get_jwt_identity()
    data = request.get_json()

    bookmark = Bookmark(**data)
    bookmark.user_id = user_id
    db.session.add(bookmark)
    db.session.commit()
    return jsonify(bookmark.to_dict()),HTTP_200_OK

@bookmarks.get("/")
@jwt_required()
def get_all():
    user_id = get_jwt_identity()
    user_bookmarks = Bookmark.query.filter_by(user_id=user_id).all()

    # Convert each bookmark object to dict
    bookmarks_list = [bookmark.to_dict() for bookmark in user_bookmarks]

    return jsonify(bookmarks_list), HTTP_200_OK