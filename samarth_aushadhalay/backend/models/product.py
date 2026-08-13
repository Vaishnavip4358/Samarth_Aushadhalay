from backend.database import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "weight": self.weight,
            "image": self.image
        }
