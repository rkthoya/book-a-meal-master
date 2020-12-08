import json
from app.models import Blacklist, User, UserType 
from flask_restless import ProcessingException
from app.validators import Valid, AuthorizationError
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_raw_jwt
)


auth = Blueprint('auth', __name__)


@jwt_required
def default_auth(**kwargs):
    """ 
    We use this empty function to as a preprocessor in JWT restless
    in order to include the @jwt_required decorator. That way, we
    can gaurd our API endpoints.
    """
    pass

@jwt_required
def caterer_auth(**kwargs):
    """ 
    This is similar to caterer_auth with the extra requirement of a user 
    being a caterer
    """
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user.is_caterer():
        raise AuthorizationError('Unauthorized access to a non-caterer')


@auth.route('/api/v1/auth/signup', methods=['POST'])
def register():
    
    if not request.is_json:
        return jsonify({'message': 'Request should be JSON'}), 400

    

    

    try:
        Valid.user()
    except ProcessingException as err:
        return jsonify({'message': err.description}), 400

    user = User(
        username=request.json['username'],
        email=request.json['email'],
        password=request.json['password']
    )
    user.save()
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201
    return res


@auth.route('/api/v1/auth/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'message': 'Request should be JSON'}), 400

    if not request.json.get('email'):
        return jsonify({'errors': ['Email is required']}), 400
    if not request.json.get('password'):
        return jsonify({'errors': ['Password is required']}), 400

    user = User.query.filter_by(email=request.json['email']).first()
    if not user or not user.validate_password(request.json['password']):
        return jsonify({'errors': ['Invalid credentials']}), 400

    access_token = create_access_token(identity=request.json['email'])
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200

@auth.route('/api/v1/auth/get', methods=['GET'])
@jwt_required
def get_user():
    if not request.is_json:
        return jsonify({'message': 'Request should be JSON'}), 400

    user = User.query.filter_by(email=get_jwt_identity()).first()
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


@auth.route('/api/v1/auth/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist = Blacklist(token=jti)
    blacklist.save()
    return jsonify({'message': 'Successfully logged out.'}), 200
