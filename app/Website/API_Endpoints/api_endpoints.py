from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

api_bp = Blueprint("api", __name__, template_folder="templates")

@api_bp.route("/auth/login", methods=["POST"])
def login():
    content_type = request.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return jsonify({"error": "Invalid data type"}), 400
    data = request.get_json(silent=True)
    
    if data is None:
        return jsonify({"error": "Invalid/Missing JSON"}), 400
    
    username = data.get("username")
    password = data.get("password")
    print(f"Received username: {username}, password: {password}")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user_id = "1" 
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    print(f"Returned: access token: {access_token}, refresh_token: {refresh_token}")
    
    return jsonify(access_token=access_token, refresh_token=refresh_token)
    
@api_bp.route("/assignments/get/all", methods=["POST"])
@jwt_required()
def assignments_get_all():
    print(f"Authorization header: {request.headers.get("Authorization")}")
    print(f"Content type {request.content_type}")
    ## JWT verification -> 401 unauthorized if fails
    #current_user = get_jwt_identity()
    print("Verified")
    return jsonify("Test"), 200
