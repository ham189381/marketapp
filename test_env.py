# test_env.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Check current directory
current_dir = Path.cwd()
print(f"Current directory: {current_dir}")

# Check if .env exists
env_file = current_dir / '.env'
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    # Load .env
    load_dotenv()
    
    # Print loaded values
    print("\n📋 Loaded Environment Variables:")
    print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'SET' if os.getenv('MAIL_PASSWORD') else 'NOT SET'}")
    print(f"MAIL_DEFAULT_SENDER: {os.getenv('MAIL_DEFAULT_SENDER')}")
    print(f"MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
    print(f"CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
else:
    print("❌ .env file not found!")
    print(f"Looking for: {env_file}")
    
    # Try to create it
    create = input("Would you like to create .env file now? (y/n): ")
    if create.lower() == 'y':
        with open('.env', 'w') as f:
            f.write('''MAIL_USERNAME=kasagaibra@gmail.com
MAIL_PASSWORD=rfjnwiffbnmupqkz
MAIL_DEFAULT_SENDER=kasagaibra@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_DEBUG=True
MAIL_SUPPRESS_SEND=False
SECRET_KEY=fcc0c7191c9768e52b1fe1e8e4863b0f7895d2511684828c07a82b85e7a57516
CLOUDINARY_CLOUD_NAME=df8mj7a7d
CLOUDINARY_API_KEY=472983627877217
CLOUDINARY_API_SECRET=qU0fIsZHNVxO36UCTvaGSKXVjno
DATABASE_URL=sqlite:///markets.db
''')
        print("✅ .env file created! Run this script again.")