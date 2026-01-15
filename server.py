import os
from flask import Flask, render_template, request, jsonify
from flask_login import current_user, login_required
from logger import setup_logger
from models import db, CartItem
from auth import auth_bp, init_oauth

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="templates/source",
    static_url_path="/source",
)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# Initialize extensions
db.init_app(app)
init_oauth(app)
app.register_blueprint(auth_bp)

setup_logger(app)

# Create tables
with app.app_context():
    db.create_all()


@app.before_request
def log_request_info():
    app.logger.info(
        'Request: %s %s from %s',
        request.method,
        request.path,
        request.remote_addr
    )


@app.route("/")
def index():
    return render_template("index.html", active_page=None)


@app.route("/home")
def home():
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product_price * item.quantity for item in cart_items)
    else:
        cart_items = []
        total = 0
    return render_template("home.html", active_page="home", cart_items=cart_items, cart_total=total)


@app.route("/pricing")
def pricing():
    return render_template("pricing.html", active_page="pricing")


# Cart API Routes
@app.route("/api/cart", methods=["GET"])
@login_required
def get_cart():
    """Get all items in the cart for the current user."""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product_price * item.quantity for item in cart_items)
    return jsonify({
        'items': [item.to_dict() for item in cart_items],
        'total': total
    })


@app.route("/api/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    """Add item to cart for the current user."""
    data = request.get_json()
    
    if not data or 'product_name' not in data or 'product_price' not in data:
        return jsonify({'error': 'Missing product_name or product_price'}), 400
    
    try:
        product_price = float(data['product_price'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid product_price'}), 400
    
    # Check if item already exists for this user
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_name=data['product_name']
    ).first()
    
    if existing_item:
        existing_item.quantity += 1
        db.session.commit()
        app.logger.info(f"Updated quantity for {data['product_name']} (user: {current_user.id})")
        return jsonify(existing_item.to_dict()), 200
    
    new_item = CartItem(
        user_id=current_user.id,
        product_name=data['product_name'],
        product_price=product_price,
        quantity=1
    )
    db.session.add(new_item)
    db.session.commit()
    
    app.logger.info(f"Added {data['product_name']} to cart (user: {current_user.id})")
    return jsonify(new_item.to_dict()), 201


@app.route("/api/cart/update/<int:item_id>", methods=["PUT"])
@login_required
def update_cart_item(item_id):
    """Update quantity of cart item for the current user."""
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return jsonify({'error': 'Missing quantity'}), 400
    
    try:
        quantity = int(data['quantity'])
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity'}), 400
    
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item.quantity = quantity
    db.session.commit()
    
    app.logger.info(f"Updated {item.product_name} quantity to {quantity} (user: {current_user.id})")
    return jsonify(item.to_dict()), 200


@app.route("/api/cart/remove/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart for the current user."""
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    product_name = item.product_name
    db.session.delete(item)
    db.session.commit()
    
    app.logger.info(f"Removed {product_name} from cart (user: {current_user.id})")
    return jsonify({'message': f'{product_name} removed from cart'}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)