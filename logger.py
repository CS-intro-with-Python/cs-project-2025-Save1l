import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(app):
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.INFO)
    sqlalchemy_handler = RotatingFileHandler(
        'logs/db.log',
        maxBytes=10240000,
        backupCount=5
    )
    sqlalchemy_handler.setFormatter(formatter)
    sqlalchemy_logger.addHandler(sqlalchemy_handler)
    

    app.logger.info('Logger initialized')