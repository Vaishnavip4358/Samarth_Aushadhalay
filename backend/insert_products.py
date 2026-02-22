import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import db
from backend.models.product import Product
from backend.models.user import User # Assuming User model also uses SQLAlchemy
from flask import Flask
from backend.app import app # Import the app instance to use its context
from flask_bcrypt import Bcrypt

def setup_database_with_sqlalchemy():
    with app.app_context():
        # Clear existing products to avoid duplicates during testing
        # In a real application, you might want a more sophisticated seeding strategy
        Product.query.delete()
        User.query.delete()
        db.session.commit()
        print("Cleared existing products and users.")

        # Insert dummy product data
        products_to_insert = [
            Product(name="Balguti Syrup", price=250.0, weight="200ml", image="img/balguti syrup.jfif"),
            Product(name="Facepack 1", price=150.0, weight="50g", image="img/facepack1.jfif"),
            Product(name="Facepack 2", price=180.0, weight="75g", image="img/facepack2.png"),
            Product(name="Paripathadi Kadha", price=300.0, weight="150ml", image="img/paripathadi kadha.jfif"),
            Product(name="Pyroz", price=120.0, weight="30g", image="img/pyroz.jfif"),
            Product(name="Varunadi Kadha", price=280.0, weight="100ml", image="img/varunadi kadha.jfif"),
            Product(name="Vasavleh", price=400.0, weight="250g", image="img/vasavleh.jfif")
        ]
        db.session.add_all(products_to_insert)
        db.session.commit()
        print(f"Inserted {len(products_to_insert)} dummy product items.")

        # Insert a dummy user
        # Initialize Bcrypt within the app context
        bcrypt_instance = Bcrypt(app)
        hashed_password = bcrypt_instance.generate_password_hash("testpassword").decode('utf-8')
        dummy_user = User(username="testuser", password=hashed_password)
        db.session.add(dummy_user)
        db.session.commit()
        print("Dummy user 'testuser' inserted with hashed password.")


if __name__ == '__main__':
    print("Setting up the database with SQLAlchemy...")
    setup_database_with_sqlalchemy()
    print("Database setup complete.")
