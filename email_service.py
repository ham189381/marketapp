# email_service.py
from flask_mail import Mail, Message
from flask import render_template_string
import re

class EmailService:
    def __init__(self):
        self.mail = None
        self.is_configured = False
        self.default_sender = None
        
    def init_app(self, app):
        """Initialize Flask-Mail with app config"""
        try:
            self.mail = Mail(app)
            self.default_sender = app.config.get('MAIL_DEFAULT_SENDER')
            self.is_configured = True
            print("✅ Email service configured successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize Email service: {e}")
            self.is_configured = False
    
    def send_order_notification_to_market(self, order, market):
        """Send order details via email to the market"""
        if not self.is_configured:
            print("⚠️ Email service not configured. Notification not sent.")
            return False
        
        if not market.email:
            print("❌ Market has no email address.")
            return False
        
        try:
            # Create email subject
            subject = f"🛒 NEW ORDER #{order.id} - {market.name}"
            
            # Create email body (HTML)
            html_body = self._create_market_order_html(order, market)
            text_body = self._create_market_order_text(order, market)
            
            # Send email
            msg = Message(
                subject=subject,
                sender=self.default_sender,
                recipients=[market.email],
                html=html_body,
                body=text_body
            )
            
            self.mail.send(msg)
            print(f"✅ Email notification sent to {market.email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email notification: {e}")
            return False
    
    def send_order_confirmation_to_customer(self, order, market):
        """Send confirmation email to customer"""
        if not self.is_configured:
            print("⚠️ Email service not configured. Customer confirmation not sent.")
            return False
        
        if not order.customer_email:
            print("❌ Customer has no email address.")
            return False
        
        try:
            subject = f"✅ Order Confirmation #{order.id} - {market.name}"
            
            html_body = self._create_customer_confirmation_html(order, market)
            text_body = self._create_customer_confirmation_text(order, market)
            
            msg = Message(
                subject=subject,
                sender=self.default_sender,
                recipients=[order.customer_email],
                html=html_body,
                body=text_body
            )
            
            self.mail.send(msg)
            print(f"✅ Order confirmation sent to {order.customer_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending customer confirmation: {e}")
            return False
    
    def send_status_update_to_customer(self, order, market, status):
        """Send status update email to customer"""
        if not self.is_configured:
            return False
        
        if not order.customer_email:
            print("❌ Customer has no email address.")
            return False
        
        try:
            status_emoji = {
                'processing': '🔄',
                'completed': '✅',
                'cancelled': '❌'
            }.get(status, '📦')
            
            subject = f"{status_emoji} Order #{order.id} Status Update"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
                    .content {{ padding: 20px; }}
                    .status {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
                    .status-processing {{ color: #17a2b8; }}
                    .status-completed {{ color: #28a745; }}
                    .status-cancelled {{ color: #dc3545; }}
                    .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📦 Order Status Update</h2>
                </div>
                <div class="content">
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Market:</strong> {market.name}</p>
                    <p><strong>Status:</strong> 
                        <span class="status status-{status}">
                            {status.upper()}
                        </span>
                    </p>
                    <div style="margin: 20px 0; padding: 15px; background: #e9ecef; border-radius: 5px;">
                        <p><strong>Items Ordered:</strong></p>
                        <pre style="white-space: pre-wrap;">{order.items_needed}</pre>
                    </div>
                    <p>Thank you for shopping with us! 🙏</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Market App.</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Order Status Update
            
            Order ID: #{order.id}
            Market: {market.name}
            Status: {status.upper()}
            
            Items Ordered:
            {order.items_needed}
            
            Thank you for shopping with us! 🙏
            """
            
            msg = Message(
                subject=subject,
                sender=self.default_sender,
                recipients=[order.customer_email],
                html=html_body,
                body=text_body
            )
            
            self.mail.send(msg)
            print(f"✅ Status update sent to {order.customer_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending status update: {e}")
            return False
    
    def _create_market_order_html(self, order, market):
        """Create HTML email for market"""
        items_list = order.items_needed.replace('\n', '<br>')
        
        return f"""
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
                .location {{ background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; }}
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
                    <p><strong>Status:</strong> <span class="status-badge">{order.status.upper()}</span></p>
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
                    <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 5px;">{items_list}</pre>
                </div>
                
                {f'''
                <div class="location">
                    <h3>📍 Location</h3>
                    <p><strong>Address:</strong> {order.location_address}</p>
                    {f'<p><strong>Google Maps:</strong> <a href="https://www.google.com/maps?q={order.latitude},{order.longitude}">View Location</a></p>' if order.latitude and order.longitude else ''}
                </div>
                ''' if order.location_address or (order.latitude and order.longitude) else ''}
                
                <div class="order-details">
                    <h3>🏪 Market Information</h3>
                    <p><strong>Name:</strong> {market.name}</p>
                    <p><strong>District:</strong> {market.district}</p>
                    <p><strong>Town:</strong> {market.town}</p>
                    <p><strong>Phone:</strong> {market.phone}</p>
                </div>
            </div>
            <div class="footer">
                <p>Please prepare these items as soon as possible.</p>
                <p>You can reply to this email or call the customer directly.</p>
            </div>
        </body>
        </html>
        """
    
    def _create_market_order_text(self, order, market):
        """Create plain text email for market"""
        items = order.items_needed.replace('\n', '\n• ')
        if not items.startswith('• '):
            items = '• ' + items
        
        return f"""
NEW ORDER ALERT!

Order ID: #{order.id}
Status: {order.status.upper()}
Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}

Customer Information:
- Name: {order.customer_name}
- Phone: {order.customer_phone}
{'- Email: ' + order.customer_email if order.customer_email else ''}

Items Needed:
{items}

Location: {order.location_address or 'Not provided'}

Market: {market.name}
District: {market.district}
Town: {market.town}

Please prepare these items as soon as possible.
You can reply to this email or call the customer directly.
"""
    
    def _create_customer_confirmation_html(self, order, market):
        """Create HTML confirmation email for customer"""
        items_list = order.items_needed.replace('\n', '<br>')
        
        return f"""
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
                    <p><strong>Status:</strong> <span class="status-badge">{order.status.upper()}</span></p>
                </div>
                
                <div class="item-list">
                    <h3>📋 Items Ordered</h3>
                    <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 5px;">{items_list}</pre>
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
    
    def _create_customer_confirmation_text(self, order, market):
        """Create plain text confirmation email for customer"""
        items = order.items_needed.replace('\n', '\n• ')
        if not items.startswith('• '):
            items = '• ' + items
        
        return f"""
Order Confirmation

Dear {order.customer_name},

Thank you for your order from {market.name}!

Order ID: #{order.id}
Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
Status: {order.status.upper()}

Items Ordered:
{items}

Market: {market.name}
Location: {market.district}, {market.town}
Market Phone: {market.phone}

The market has been notified of your order.
You will receive updates on your order status.

Thank you for using our service! 🙏
"""

# Initialize Email service
email_service = EmailService()