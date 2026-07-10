from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime
import base64
from config import Config
from models import db, Market, Order
from cloudinary_utils import init_cloudinary, upload_to_cloudinary

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Cloudinary
init_cloudinary(app)

# Initialize email
mail = Mail(app)

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()

# Helper functions
def save_file(file, folder):
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{timestamp}_{name}{ext}"
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filename
    return None

def save_base64_file(base64_data, folder, file_type='image'):
    if base64_data and ',' in base64_data:
        header, data = base64_data.split(',', 1)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if file_type == 'image':
            filename = f"{timestamp}.jpg"
        else:
            filename = f"{timestamp}.webm"
            
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(data))
        return filename
    return None

# Cloudinary upload helper function
def upload_to_cloudinary_helper(file_data, file_type='image', folder='markets'):
    """
    Upload file to Cloudinary instead of local storage
    
    Args:
        file_data: Base64 data or file object
        file_type: 'image' or 'video'
        folder: Cloudinary folder name
    
    Returns:
        str: Cloudinary URL or None if failed
    """
    if not file_data:
        return None
    
    try:
        result = upload_to_cloudinary(file_data, folder, file_type)
        if result['success']:
            return result['url']
        else:
            print(f"Cloudinary upload failed: {result.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None

def validate_phone(phone):
    # Simple phone validation (you can adjust the pattern)
    pattern = re.compile(r'^[0-9+\-\s()]{7,20}$')
    return pattern.match(phone)

# Email helper functions
def send_order_email(order, market):
    """Send order notification email to market"""
    try:
        # Create email content
        subject = f"🛒 NEW ORDER #{order.id} - {market.name}"
        
        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .content {{ padding: 20px; }}
                .order-details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .item-list {{ background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; border-radius: 5px; }}
                .status-badge {{ display: inline-block; padding: 5px 15px; background: #ffc107; border-radius: 20px; color: #000; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🛒 NEW ORDER ALERT!</h2>
            </div>
            <div class="content">
                <div class="order-details">
                    <h3>Order Details</h3>
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Status:</strong> <span class="status-badge">PENDING</span></p>
                    <p><strong>Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div class="order-details">
                    <h3>Customer Information</h3>
                    <p><strong>Name:</strong> {order.customer_name}</p>
                    <p><strong>Phone:</strong> {order.customer_phone}</p>
                    {f'<p><strong>Email:</strong> {order.customer_email}</p>' if order.customer_email else ''}
                </div>
                
                <div class="item-list">
                    <h3>📋 Items Needed</h3>
                    <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 5px;">{order.items_needed}</pre>
                </div>
                
                {f'''
                <div class="order-details">
                    <h3>📍 Location</h3>
                    <p><strong>Address:</strong> {order.location_address}</p>
                    {f'<p><strong>Google Maps:</strong> <a href="https://www.google.com/maps?q={order.latitude},{order.longitude}">View Location</a></p>' if order.latitude and order.longitude else ''}
                </div>
                ''' if order.location_address or (order.latitude and order.longitude) else ''}
            </div>
            <div class="footer">
                <p>Please prepare these items as soon as possible.</p>
                <p>You can reply to this email or call the customer directly.</p>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_body = f"""
NEW ORDER ALERT!

Order ID: #{order.id}
Status: PENDING
Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}

Customer Information:
- Name: {order.customer_name}
- Phone: {order.customer_phone}
{'- Email: ' + order.customer_email if order.customer_email else ''}

Items Needed:
{order.items_needed}

Location: {order.location_address or 'Not provided'}

Please prepare these items as soon as possible.
You can reply to this email or call the customer directly.
"""
        
        # Send email
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[market.email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_customer_confirmation(order, market):
    """Send confirmation email to customer"""
    try:
        subject = f"✅ Order Confirmation #{order.id} - {market.name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .content {{ padding: 20px; }}
                .order-details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .item-list {{ background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; border-radius: 5px; }}
                .status-badge {{ display: inline-block; padding: 5px 15px; background: #ffc107; border-radius: 20px; color: #000; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>✅ Order Confirmation</h2>
            </div>
            <div class="content">
                <p>Dear {order.customer_name},</p>
                
                <p>Thank you for your order from <strong>{market.name}</strong>!</p>
                
                <div class="order-details">
                    <h3>Order Details</h3>
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>Status:</strong> <span class="status-badge">PENDING</span></p>
                </div>
                
                <div class="item-list">
                    <h3>📋 Items Ordered</h3>
                    <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 5px;">{order.items_needed}</pre>
                </div>
                
                <div class="order-details">
                    <p><strong>Market:</strong> {market.name}</p>
                    <p><strong>Location:</strong> {market.district}, {market.town}</p>
                    <p><strong>Market Phone:</strong> {market.phone}</p>
                </div>
                
                <p>The market has been notified of your order.</p>
                <p>You will receive updates on your order status.</p>
                
                <p style="margin-top: 20px;">Thank you for using our service! 🙏</p>
            </div>
            <div class="footer">
                <p>This is an automated message from Market App.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Order Confirmation

Dear {order.customer_name},

Thank you for your order from {market.name}!

Order ID: #{order.id}
Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
Status: PENDING

Items Ordered:
{order.items_needed}

Market: {market.name}
Location: {market.district}, {market.town}
Market Phone: {market.phone}

The market has been notified of your order.
You will receive updates on your order status.

Thank you for using our service! 🙏
"""
        
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[order.customer_email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending customer confirmation: {e}")
        return False

@app.route('/')
def index():
    markets = Market.query.order_by(Market.created_at.desc()).all()
    return render_template('index.html', markets=markets)

@app.route('/register', methods=['GET', 'POST'])
def register_market():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            market_type = request.form.get('market_type')
            district = request.form.get('district', '').strip()
            town = request.form.get('town', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            
            # Manual validation
            errors = []
            
            if not name:
                errors.append('Market name is required')
            elif len(name) > 100:
                errors.append('Market name must be less than 100 characters')
            
            if not district:
                errors.append('District is required')
            
            if not town:
                errors.append('Town is required')
            
            if not phone:
                errors.append('Phone number is required')
            elif not validate_phone(phone):
                errors.append('Invalid phone number format')
            
            if market_type not in ['supermarket', 'local']:
                errors.append('Invalid market type')
            
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('register_market.html')
            
            # Handle images and video - Upload to Cloudinary
            image1_url = None
            image2_url = None
            video_url = None
            
            # Check for base64 data from camera
            image1_data = request.form.get('image1_data')
            image2_data = request.form.get('image2_data')
            video_data = request.form.get('video_data')
            
            # Upload to Cloudinary instead of local storage
            if image1_data:
                image1_url = upload_to_cloudinary_helper(image1_data, 'image', 'market_images')
            elif 'image1' in request.files and request.files['image1'].filename:
                image1_url = upload_to_cloudinary_helper(request.files['image1'], 'image', 'market_images')
            
            if image2_data:
                image2_url = upload_to_cloudinary_helper(image2_data, 'image', 'market_images')
            elif 'image2' in request.files and request.files['image2'].filename:
                image2_url = upload_to_cloudinary_helper(request.files['image2'], 'image', 'market_images')
            
            if video_data:
                video_url = upload_to_cloudinary_helper(video_data, 'video', 'market_videos')
            elif 'video' in request.files and request.files['video'].filename:
                video_url = upload_to_cloudinary_helper(request.files['video'], 'video', 'market_videos')
            
            # Create market entry with Cloudinary URLs and email
            market = Market(
                name=name,
                market_type=market_type,
                district=district,
                town=town,
                phone=phone,
                email=email,
                image1=image1_url,
                image2=image2_url,
                video=video_url
            )
            
            db.session.add(market)
            db.session.commit()
            
            flash('Market registered successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering market: {str(e)}', 'danger')
            return render_template('register_market.html')
    
    return render_template('register_market.html')

@app.route('/market/<int:market_id>')
def market_detail(market_id):
    market = Market.query.get_or_404(market_id)
    return render_template('market_detail.html', market=market)

@app.route('/order/<int:market_id>', methods=['GET', 'POST'])
def place_order(market_id):
    market = Market.query.get_or_404(market_id)
    
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            customer_email = request.form.get('customer_email', '').strip()
            items_needed = request.form.get('items_needed', '').strip()
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            location_address = request.form.get('location_address', '').strip()
            
            # Manual validation
            errors = []
            
            if not customer_name:
                errors.append('Customer name is required')
            elif len(customer_name) > 100:
                errors.append('Customer name must be less than 100 characters')
            
            if not customer_phone:
                errors.append('Customer phone is required')
            elif not validate_phone(customer_phone):
                errors.append('Invalid phone number format')
            
            if not items_needed:
                errors.append('Items needed list is required')
            
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('order_form.html', market=market)
            
            order = Order(
                market_id=market_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                items_needed=items_needed,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                location_address=location_address
            )
            
            db.session.add(order)
            db.session.commit()
            
            # Send email notifications
            email_sent = False
            customer_email_sent = False
            
            # Send to market if they have email
            if market.email:
                email_sent = send_order_email(order, market)
            
            # Send confirmation to customer if they provided email
            if customer_email:
                customer_email_sent = send_customer_confirmation(order, market)
            
            # Flash appropriate messages
            if email_sent and customer_email_sent:
                flash('✅ Order placed successfully! Both market and customer have been notified via email.', 'success')
            elif email_sent:
                flash('✅ Order placed successfully! Market notified via email.', 'success')
            elif customer_email_sent:
                flash('✅ Order placed successfully! Confirmation sent to your email.', 'success')
            else:
                flash('✅ Order placed successfully! (Email notifications could not be sent.)', 'warning')
            
            return redirect(url_for('market_detail', market_id=market_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error placing order: {str(e)}', 'danger')
            return render_template('order_form.html', market=market)
    
    return render_template('order_form.html', market=market)

@app.route('/api/markets')
def get_markets():
    markets = Market.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'market_type': m.market_type,
        'district': m.district,
        'town': m.town,
        'phone': m.phone,
        'image1': m.image1,
        'image2': m.image2,
        'video': m.video,
        'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for m in markets])

# Routes to deal with all the orders

@app.route('/orders')
def view_orders():
    """Display all orders"""
    # Get all orders with market information
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # Get unique market IDs for statistics
    market_ids = set(order.market_id for order in orders)
    total_markets = len(market_ids)
    
    return render_template('orders.html', 
                         orders=orders, 
                         total_orders=len(orders),
                         total_markets=total_markets)

@app.route('/orders/market/<int:market_id>')
def view_market_orders(market_id):
    """Display orders for a specific market"""
    market = Market.query.get_or_404(market_id)
    orders = Order.query.filter_by(market_id=market_id)\
                       .order_by(Order.created_at.desc()).all()
    
    return render_template('market_orders.html', 
                         market=market, 
                         orders=orders)

@app.route('/api/orders')
def get_orders_api():
    """API endpoint to get all orders"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': o.id,
        'market_id': o.market_id,
        'market_name': o.market.name if o.market else None,
        'customer_name': o.customer_name,
        'customer_phone': o.customer_phone,
        'customer_email': o.customer_email,
        'items_needed': o.items_needed,
        'latitude': o.latitude,
        'longitude': o.longitude,
        'location_address': o.location_address,
        'status': getattr(o, 'status', 'pending'),
        'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for o in orders])

# Optional: Add order status update route
@app.route('/order/status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    """Update order status (for admin/market owners)"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    else:
        flash('Invalid status!', 'danger')
    
    return redirect(url_for('view_orders'))

# Admin-only order management page
@app.route('/admin/orders')
def admin_orders():
    """Admin view with statistics and management"""
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    
    orders_by_market = db.session.query(
        Market.name, 
        db.func.count(Order.id).label('order_count')
    ).join(Order).group_by(Market.id).all()
    
    return render_template('admin_orders.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         orders_by_market=orders_by_market)

if __name__ == '__main__':
    app.run(debug=True)