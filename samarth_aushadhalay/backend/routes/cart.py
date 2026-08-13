from flask import Blueprint, session, jsonify, request
from backend.database import db
from backend.models.product import Product
from backend.models.user import User
from backend.models.order import Cart
from .auth import login_required

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    data = request.get_json()
    product_id_str = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id_str:
        return jsonify({'message': 'Product ID is required'}), 400

    try:
        product_id = int(product_id_str)
    except ValueError:
        return jsonify({'message': 'Invalid Product ID format. Must be an integer.'}), 400

    product = Product.query.get(product_id)

    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Check if item already exists in user's cart
    existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if existing_cart_item:
        # Update quantity
        existing_cart_item.quantity += quantity
        db.session.commit()
        message = 'Product quantity updated in cart'
    else:
        # Add new item to cart
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()
        message = 'Product added to cart'
    
    return jsonify({'message': message}), 200

@cart_bp.route('/', methods=['GET'])
@login_required
def get_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    # Get all cart items for the user
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    # Convert to the format expected by frontend
    cart_data = {}
    for item in cart_items:
        cart_data[str(item.product_id)] = {
            'product_id': item.product_id,
            'name': item.product.name,
            'price': item.product.price,
            'image': item.product.image,
            'quantity': item.quantity
        }
    
    return jsonify({'cart': cart_data}), 200

@cart_bp.route('/remove/<string:product_id_str>', methods=['POST'])
@login_required
def remove_from_cart(product_id_str):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    try:
        product_id = int(product_id_str)
    except ValueError:
        return jsonify({'message': 'Invalid Product ID format'}), 400

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if not cart_item:
        return jsonify({'message': 'Product not found in cart'}), 404
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        message = 'Item quantity reduced'
    else:
        db.session.delete(cart_item)
        message = 'Item removed from cart'
    
    db.session.commit()
    return jsonify({'message': message}), 200

@cart_bp.route('/update/<string:product_id_str>', methods=['POST'])
@login_required
def update_cart_item(product_id_str):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    data = request.get_json()
    quantity = int(data.get('quantity', 1))

    if quantity <= 0:
        return jsonify({'message': 'Quantity must be positive'}), 400

    try:
        product_id = int(product_id_str)
    except ValueError:
        return jsonify({'message': 'Invalid Product ID format'}), 400

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if not cart_item:
        return jsonify({'message': 'Product not found in cart'}), 404
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({'message': 'Cart updated'}), 200

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear all items from user's cart"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared'}), 200
