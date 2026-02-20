"""
Test script to verify Django setup before migrations
"""
import os
import sys

print("=" * 60)
print("DJANGO SETUP VERIFICATION")
print("=" * 60)

# Test 1: Python version
print("\n1. Python Version:")
print(f"{sys.version}")

# Test 2: Check if venv is activated
print("\n2. Virtual Environment:")
if hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
):
    print("Virtual environment is activated")
else:
    print("Virtual environment is NOT activated!")
    print("Run: venv\\Scripts\\activate")

# Test 3: Required packages
print("\n3. Required Packages:")
required_packages = {
    'django': 'Django',
    'pymysql': 'PyMySQL',
    'decouple': 'python-decouple'
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"{package_name} is installed")
    except ImportError:
        print(f"{package_name} is NOT installed!")
        print(f"Run: pip install {package_name}")

# Test 4: .env file
print("\n4. Environment File:")
if os.path.exists('.env'):
    print(".env file exists")
    
    # Check if it has required variables
    with open('.env', 'r') as f:
        content = f.read()
        required_vars = [
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_HOST',
            'DB_PORT'
        ]
        for var in required_vars:
            if var in content:
                print(f"{var} is set")
            else:
                print(f"{var} is missing!")
else:
    print(".env file does NOT exist!")
    print("Run: copy .env.example .env")

# Test 5: Database connection
print("\n5. Database Connection:")
try:
    import pymysql
    from decouple import config
    
    connection = pymysql.connect(
        host=config('DB_HOST', default='localhost'),
        user=config('DB_USER', default='ecommerce_user'),
        password=config('DB_PASSWORD', default='ecommerce_password123'),
        database=config('DB_NAME', default='ecommerce_db')
    )
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print("Database connection failed!")
    print(f"Error: {e}")

# Test 6: Django settings
print("\n6. Django Settings:")
try:
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'ecommerce_project.settings'
    )
    import django
    django.setup()
    print("Django settings loaded successfully")
except Exception as e:
    print("Django settings failed to load!")
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nIf all checks pass, you can run:")
print("  python manage.py migrate")