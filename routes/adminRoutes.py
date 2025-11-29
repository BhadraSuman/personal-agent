from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models.adminModel import Admin, MailSettings
from models.settingModel import Setting, SkillSetting, AdminSkillSet

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from mongoengine.errors import DoesNotExist, ValidationError

from utils.response import make_response
from utils.agentToken import role_required

admin_bp = Blueprint('admin_bp', __name__)

# Register admin
# @admin_bp.route('/register', methods=['POST'])
# def register_admin():
#     data = request.get_json()
#     if Admin.objects(username=data['username']).first():
#         return jsonify({"msg": "Admin already exists"}), 400

#     admin = Admin(username=data['username'])
#     admin.set_password(data['password'])
#     admin.save()
#     return jsonify({"msg": "Admin created successfully"}), 201

# Login admin
@admin_bp.route('/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    admin = Admin.objects(username=data['username']).first()
    setting = Setting.objects.first()
    
    # Check if admin exists
    if not admin:
        return jsonify({"msg": "Invalid credentials"}), 401

    # Prevent deleted users from logging in
    if admin.deleted:
        return jsonify({"msg": "This account has been deleted. Contact support."}), 403

    # Check password or master key
    if setting.master_key != data['password']:
        if not admin.check_password(data['password']):
            return jsonify({"msg": "Invalid credentials"}), 401

    # Add role + deleted status in token claims
    additional_claims = {
        "role": admin.role,
        "deleted": admin.deleted
    }

    access_token = create_access_token(
        identity=str(admin.id),
        additional_claims=additional_claims,
        expires_delta=timedelta(days=1)
    )

    return make_response(
        data={"token": access_token, "user": admin.to_mongo()},
        msg="Login successful",
        status_code=200
    )

# Get current admin profile
@admin_bp.route('/me', methods=['GET'])
@jwt_required()
@role_required(["admin","superadmin"])
def get_profile():
    admin_id = get_jwt_identity()
    admin = Admin.objects(id=admin_id).first()

    if not admin:
        return jsonify({"msg": "Admin not found"}), 404

    return jsonify({
        "id": str(admin.id),
        "name": admin.name,
        "username": admin.username,
        "email": admin.email,
        "phone": admin.phone,
        "role": admin.role,
        "created_at": admin.created_at.isoformat() if admin.created_at else None
    }), 200




    
