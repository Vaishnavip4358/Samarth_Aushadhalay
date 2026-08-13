# routes/auth.py
from flask import Blueprint, request, jsonify, session, current_app, redirect, url_for
from functools import wraps
from backend.database import db
from backend.models.user import User
# from flask_mail import Message # Removed
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

auth_bp = Blueprint('auth', __name__)

# Helper function to generate password reset token
def get_reset_token(user, expires_sec=1800): # Token expires in 30 minutes
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'user_id': user.id}, salt='password-reset-salt')

# Helper function to verify password reset token
def verify_reset_token(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='password-reset-salt', max_age=1800) # 30 minutes expiration
        user_id = data['user_id']
    except (SignatureExpired, BadTimeSignature):
        return None
    return User.query.get(user_id)

# Removed send_reset_email function as per user request

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    bcrypt = current_app.extensions['bcrypt']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    bcrypt = current_app.extensions['bcrypt']
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Successful login: set session
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.username
    session.permanent = True  # uses PERMANENT_SESSION_LIFETIME
    return jsonify({'message': 'Login successful'}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# Forgot Password Request (Insecure - no email verification)
@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password_request():
    data = request.get_json() or {}
    identifier = (data.get('identifier') or '').strip().lower()

    user = User.query.filter_by(username=identifier).first()
    
    if user:
        token = get_reset_token(user)
        # Directly redirect to the reset password page with the token
        return jsonify({'redirect_url': url_for('reset_password_page', token=token, _external=False)})
    else:
        # If user not found, redirect to the reset page without a token or with a generic error token
        # This prevents user enumeration, but also doesn't immediately show a user-friendly error
        # The client-side JS will need to handle the case of a missing token
        return jsonify({'redirect_url': url_for('reset_password_page', token='invalid_token', _external=False)})


# Password Reset
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = verify_reset_token(token)
    if user is None:
        return jsonify({'message': 'That is an invalid or expired token'}), 400
    
    if request.method == 'POST':
        data = request.get_json() or {}
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({'message': 'New password is required'}), 400

        bcrypt = current_app.extensions['bcrypt']
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return jsonify({'message': 'Your password has been updated!'}), 200
    else: # GET request
        return redirect(url_for('reset_password_page', token=token))

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'user_id': session.get('user_id'), 'username': session.get('username')}), 200

