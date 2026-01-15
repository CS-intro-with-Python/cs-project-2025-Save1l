from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for OAuth authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'


class CartItem(db.Model):
    """Shopping cart item model."""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<CartItem {self.product_name} x{self.quantity}>'
    
    def to_dict(self):
        """Convert cart item to dictionary for JSON response."""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_price': self.product_price,
            'quantity': self.quantity,
            'total': self.product_price * self.quantity
        }
