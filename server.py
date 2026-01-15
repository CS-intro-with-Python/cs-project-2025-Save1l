import os
from flask import Flask, render_template, request, jsonify
from flask_login import current_user, login_required
from flask_restx import Api, Resource, fields, Namespace
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

# Initialize Swagger API
api = Api(
    app,
    version='1.0',
    title='Gaming Store API',
    description='REST API для управления корзиной покупок в Gaming Store',
    doc='/swagger',
    prefix='/api'
)

# Create namespace for cart operations
cart_ns = Namespace('cart', description='Операции с корзиной покупок')
api.add_namespace(cart_ns)

# Define models for Swagger documentation
cart_item_model = api.model('CartItem', {
    'id': fields.Integer(readonly=True, description='ID товара в корзине'),
    'product_name': fields.String(required=True, description='Название товара'),
    'product_price': fields.Float(required=True, description='Цена товара'),
    'quantity': fields.Integer(description='Количество', default=1),
    'total': fields.Float(readonly=True, description='Общая стоимость позиции')
})

cart_response_model = api.model('CartResponse', {
    'items': fields.List(fields.Nested(cart_item_model), description='Список товаров в корзине'),
    'total': fields.Float(description='Общая сумма корзины')
})

add_item_model = api.model('AddItem', {
    'product_name': fields.String(required=True, description='Название товара', example='Cyberpunk 2077'),
    'product_price': fields.Float(required=True, description='Цена товара', example=59.99)
})

update_quantity_model = api.model('UpdateQuantity', {
    'quantity': fields.Integer(required=True, description='Новое количество', example=2, min=1)
})

error_model = api.model('Error', {
    'error': fields.String(description='Сообщение об ошибке')
})

message_model = api.model('Message', {
    'message': fields.String(description='Сообщение')
})

health_model = api.model('Health', {
    'status': fields.String(description='Статус приложения'),
    'database': fields.String(description='Статус базы данных')
})

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


# =============================================================================
# Cart API with Swagger Documentation
# =============================================================================

@cart_ns.route('/')
class CartList(Resource):
    @cart_ns.doc('get_cart', security='apikey')
    @cart_ns.marshal_with(cart_response_model)
    @cart_ns.response(401, 'Unauthorized')
    @login_required
    def get(self):
        """Получить все товары в корзине текущего пользователя"""
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product_price * item.quantity for item in cart_items)
        return {
            'items': [item.to_dict() for item in cart_items],
            'total': total
        }


@cart_ns.route('/add')
class CartAdd(Resource):
    @cart_ns.doc('add_to_cart', security='apikey')
    @cart_ns.expect(add_item_model)
    @cart_ns.marshal_with(cart_item_model, code=201)
    @cart_ns.response(400, 'Validation Error', error_model)
    @cart_ns.response(401, 'Unauthorized')
    @login_required
    def post(self):
        """Добавить товар в корзину"""
        data = request.get_json()
        
        if not data or 'product_name' not in data or 'product_price' not in data:
            cart_ns.abort(400, 'Missing product_name or product_price')
        
        try:
            product_price = float(data['product_price'])
        except (ValueError, TypeError):
            cart_ns.abort(400, 'Invalid product_price')
        
        # Check if item already exists for this user
        existing_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_name=data['product_name']
        ).first()
        
        if existing_item:
            existing_item.quantity += 1
            db.session.commit()
            app.logger.info(f"Updated quantity for {data['product_name']} (user: {current_user.id})")
            return existing_item.to_dict(), 200
        
        new_item = CartItem(
            user_id=current_user.id,
            product_name=data['product_name'],
            product_price=product_price,
            quantity=1
        )
        db.session.add(new_item)
        db.session.commit()
        
        app.logger.info(f"Added {data['product_name']} to cart (user: {current_user.id})")
        return new_item.to_dict(), 201


@cart_ns.route('/update/<int:item_id>')
@cart_ns.param('item_id', 'ID товара в корзине')
class CartUpdate(Resource):
    @cart_ns.doc('update_cart_item', security='apikey')
    @cart_ns.expect(update_quantity_model)
    @cart_ns.marshal_with(cart_item_model)
    @cart_ns.response(400, 'Validation Error', error_model)
    @cart_ns.response(401, 'Unauthorized')
    @cart_ns.response(404, 'Item not found', error_model)
    @login_required
    def put(self, item_id):
        """Обновить количество товара в корзине"""
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            cart_ns.abort(400, 'Missing quantity')
        
        try:
            quantity = int(data['quantity'])
            if quantity < 1:
                cart_ns.abort(400, 'Quantity must be at least 1')
        except (ValueError, TypeError):
            cart_ns.abort(400, 'Invalid quantity')
        
        item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            cart_ns.abort(404, 'Item not found')
        
        item.quantity = quantity
        db.session.commit()
        
        app.logger.info(f"Updated {item.product_name} quantity to {quantity} (user: {current_user.id})")
        return item.to_dict(), 200


@cart_ns.route('/remove/<int:item_id>')
@cart_ns.param('item_id', 'ID товара в корзине')
class CartRemove(Resource):
    @cart_ns.doc('remove_from_cart', security='apikey')
    @cart_ns.marshal_with(message_model)
    @cart_ns.response(401, 'Unauthorized')
    @cart_ns.response(404, 'Item not found', error_model)
    @login_required
    def delete(self, item_id):
        """Удалить товар из корзины"""
        item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            cart_ns.abort(404, 'Item not found')
        
        product_name = item.product_name
        db.session.delete(item)
        db.session.commit()
        
        app.logger.info(f"Removed {product_name} from cart (user: {current_user.id})")
        return {'message': f'{product_name} removed from cart'}, 200


# =============================================================================
# Health Check Endpoint
# =============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    try:
        # Проверяем подключение к базе данных
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        return jsonify({
            'status': 'unhealthy',
            'database': db_status
        }), 500
    
    return jsonify({
        'status': 'healthy',
        'database': db_status
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)