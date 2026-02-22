# app.py
import os
import sys
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_mail import Mail # Added
from backend.database import db # Import db from the new database.py

from routes.auth import auth_bp
from routes.products import product_bp
from routes.cart import cart_bp
from routes.order import order_bp

app = Flask(__name__, static_folder='static', template_folder='templates')

from datetime import timedelta

app.secret_key = os.environ.get('SECRET_KEY', 'dev-change-me')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # 'Strict' or 'Lax' recommended
    SESSION_COOKIE_SECURE=False,     # set True in production (HTTPS)
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' # Or your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')

mail = Mail(app) # Initialized Flask-Mail

# MySQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Vaishnavi%404358@localhost/samarth_aushadhalay_db' # Placeholder password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Initialize db with the app
bcrypt = Bcrypt(app)
app.extensions['bcrypt'] = bcrypt

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(order_bp, url_prefix='/api/order')

# Routes for serving HTML files
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/products.html')
def products_page():
    return render_template('products.html')

@app.route('/about.html')
def about_page():
    return render_template('about.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/cart.html')
def cart_page():
    return render_template('cart.html')

@app.route('/order_history.html')
def order_history_page():
    return render_template('order_history.html')

@app.route('/forgot_password.html')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/reset_password.html')
def reset_password_page():
    return render_template('reset_password.html')

if __name__ == '__main__':
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from backend.models.user import User
        from backend.models.product import Product
        from backend.models.order import Order, OrderItem
        db.create_all()
    app.run(debug=True)
