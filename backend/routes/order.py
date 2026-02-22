import traceback
from flask import Blueprint, session, jsonify, request, current_app as app
from backend.database import db
from backend.models.user import User # Assuming User model is used for user_id
from backend.models.product import Product # For product details if needed in OrderItem creation
from backend.models.order import Order, OrderItem
from datetime import datetime
from .auth import login_required # Import the login_required decorator

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401
        
    cart = session.get('cart')
    if not cart:
        return jsonify({'message': 'Cart is empty'}), 400

    try:
        # Calculate total and prepare items list
        total_price = 0
        order_items = []

        for product_id_str, item_details in cart.items():
            product_id = int(product_id_str) # Ensure it's an integer
            
            # Optional: re-fetch product details from DB to ensure they are current
            product = Product.query.get(product_id)
            if not product:
                # This should ideally not happen if cart validation is strong
                return jsonify({'message': f'Product with ID {product_id} not found.'}), 404

            item_total = product.price * item_details['quantity']
            total_price += item_total
            
            order_item = OrderItem(
                product_id=product_id,
                name=product.name, # Use product.name from DB
                price=product.price, # Use product.price from DB
                quantity=item_details['quantity']
            )
            order_items.append(order_item)

        # Create the order
        new_order = Order(
            user_id=user_id,
            total_price=total_price,
            created_at=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.commit() # Commit to get the order_id

        # Associate order_items with the new_order and add to session
        for item in order_items:
            item.order_id = new_order.id
            db.session.add(item)
        db.session.commit()

        # Clear the cart from the session
        session.pop('cart', None)
        session.modified = True
        
        return jsonify({'message': 'Order created successfully', 'order_id': new_order.id}), 201

    except Exception as e:
        db.session.rollback() # Rollback in case of any error
        current_app.logger.error(f"Error creating order: {e}")
        traceback.print_exc() # Print the full traceback
        return jsonify({'message': 'An error occurred during checkout.'}), 500

@order_bp.route('/history', methods=['GET'])
@login_required
def get_order_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Authentication required'}), 401

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    user_orders_data = []
    for order in orders:
        user_orders_data.append(order.to_dict()) # Use the to_dict method from the Order model
        
    return jsonify({'history': user_orders_data}), 200
