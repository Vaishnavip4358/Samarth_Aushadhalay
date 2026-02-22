from flask import Blueprint, jsonify
from backend.database import db
from backend.models.product import Product

product_bp = Blueprint('products', __name__)

@product_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    products_data = [product.to_dict() for product in products]
    return jsonify(products_data)
