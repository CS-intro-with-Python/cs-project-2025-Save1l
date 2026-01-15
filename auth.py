import os
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, current_user

from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

oauth = OAuth()
login_manager = LoginManager()


def init_oauth(app):
    """Initialize OAuth and Login Manager with the Flask app."""
    oauth.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


@auth_bp.route('/login')
def login():
    """Redirect to Google OAuth login."""
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """Handle OAuth callback from Google."""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user = User.query.filter_by(google_id=user_info['sub']).first()
            
            if not user:
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name', user_info['email']),
                    google_id=user_info['sub']
                )
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('home'))
        
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('index'))


@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
