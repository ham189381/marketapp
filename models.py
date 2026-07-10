from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    market_type = db.Column(db.String(20), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))  # Market email for order notifications
    image1 = db.Column(db.String(500))  # Cloudinary URL
    image2 = db.Column(db.String(500))  # Cloudinary URL
    video = db.Column(db.String(500))   # Cloudinary URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='market', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100))  # Customer email for confirmation
    items_needed = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_address = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)