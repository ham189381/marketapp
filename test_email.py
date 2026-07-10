# test_email.py
from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

print("=" * 50)
print("EMAIL CONFIGURATION CHECK")
print("=" * 50)
print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
print(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
print(f"MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', '')) if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
print("=" * 50)

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject='Test Email from Market App',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['kasagaibra@gmail.com'],  # CHANGE THIS to your email
            body='This is a test email to verify your Market App email configuration is working!'
        )
        mail.send(msg)
        print("✅ Test email sent successfully!")
        print("Your email functionality is WORKING! 🎉")
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        print("\n🔧 To fix this, check:")
        print("1. Your .env file exists and has correct credentials")
        print("2. MAIL_USERNAME is your Gmail address")
        print("3. MAIL_PASSWORD is your App Password (16 chars, no spaces)")
        print("4. 2-Step Verification is enabled on your Gmail")
        print("5. You're using an App Password, not your regular Gmail password")