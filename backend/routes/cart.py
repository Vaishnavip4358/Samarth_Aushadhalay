from flask import Blueprint, session, jsonify, request
from backend.database import db
from backend.models.product import Product
from backend.models.user import User # Assuming User is also needed, though not directly in cart logic

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
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

    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    # Convert product_id back to string for dictionary key consistency in session
    product_id_key = str(product_id)
    cart_item = session['cart'].get(product_id_key)

    if cart_item:
        cart_item['quantity'] += quantity
    else:
        session['cart'][product_id_key] = {
            'product_id': product_id, # Store as integer
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'quantity': quantity
        }
    session.modified = True # Mark session as modified
    return jsonify({'message': 'Product added to cart', 'cart': session['cart']}), 200

@cart_bp.route('/', methods=['GET'])
def get_cart():
    # Return the cart contents from the session
    return jsonify({'cart': session.get('cart', {})}), 200

@cart_bp.route('/remove/<string:product_id_str>', methods=['POST'])
def remove_from_cart(product_id_str):
    # No need to convert to int, as we store product_id as string key in session
    if 'cart' in session and product_id_str in session['cart']:
        cart_item = session['cart'][product_id_str]
        if cart_item['quantity'] > 1:
            cart_item['quantity'] -= 1
        else:
            del session['cart'][product_id_str]
        session.modified = True
        return jsonify({'message': 'Item quantity reduced', 'cart': session['cart']}), 200
    return jsonify({'message': 'Product not found in cart'}), 404

@cart_bp.route('/update/<string:product_id_str>', methods=['POST'])
def update_cart_item(product_id_str):
    data = request.get_json()
    quantity = int(data.get('quantity', 1))

    if quantity <= 0:
        return jsonify({'message': 'Quantity must be positive'}), 400

    if 'cart' in session and product_id_str in session['cart']:
        session['cart'][product_id_str]['quantity'] = quantity
        session.modified = True
        return jsonify({'message': 'Cart updated', 'cart': session['cart']}), 200
    return jsonify({'message': 'Product not found in cart'}), 404
