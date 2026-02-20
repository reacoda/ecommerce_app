# Django eCommerce Application

A full-featured eCommerce platform built with Django, featuring vendor and buyer roles, shopping cart, order management, and product reviews.

## Features

### Vendor Features
-  Register and login as vendor
-  Create and manage multiple stores
-  Add, edit, and delete products
-  View product inventory
-  Manage store information

### Buyer Features
-  Register and login as buyer
-  Browse all products from all stores
-  Add products to shopping cart
-  Update cart quantities
-  Complete checkout process
-  View order history
-  Leave product reviews (verified purchase badge)

### Authentication & Security
-  User registration with role selection
-  Login/logout functionality
-  Password reset with email tokens
-  Permission-based access control
-  Session-based shopping cart
-  Hashed passwords

### Email Features
-  Order confirmation emails
-  Invoice generation
-  Password reset emails

## Technology Stack

- **Backend:** Django 5.0+
- **Database:** MariaDB 11.4
- **Python:** 3.14
- **MySQL Connector:** pymysql
- **Frontend:** HTML, CSS (inline styling)

## Database Models

1. **Store** - Vendor stores
2. **Product** - Products in stores
3. **Order** - Customer orders
4. **OrderItem** - Items in orders
5. **Review** - Product reviews
6. **PasswordResetToken** - Password reset tokens

## Installation & Setup

### Prerequisites
- Python 3.12+
- MariaDB 11.2+
- pip

### Step 1: Clone/Extract Project
```bash
# Clone from Github
git clone https://github.com/reacoda/ecommerce_app.git

# Navigate to project directory
cd ecommerce_app
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Database

1. **Install MariaDB** (if not already installed)
    - Download from: https://mariadb.org/download/

2. **Create database and user:**
```bash
mysql -u root -p
```
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'ecommerce_password123';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **Create `.env` file** (copy from `.env.example`):
   
**Windows**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

4. **Edit `.env` file** with your database credentials

   Open `.env` in a text editor and update:
```env
# Database Configuration
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_password123  # ← Change this to your password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (Optional - for sending real emails)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```
**Important:** The `.env` file must be created and configured BEFORE running migrations!

### Step 6: Update Django Settings (if needed)

The `settings.py` file is already configured to read from `.env` file.
No manual changes needed if you followed Step 5.

Verify your `settings.py` has this configuration:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='ecommerce_db'),
        'USER': config('DB_USER', default='ecommerce_user'),
        'PASSWORD': config('DB_PASSWORD', default='ecommerce_password123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### Step 7: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 8: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 9: Create Groups & Test Users
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from store.models import Store, Product, Review, Order, OrderItem

# Create Groups
vendors_group, _ = Group.objects.get_or_create(name='Vendors')
buyers_group, _ = Group.objects.get_or_create(name='Buyers')

# Assign permissions
store_ct = ContentType.objects.get_for_model(Store)
product_ct = ContentType.objects.get_for_model(Product)
review_ct = ContentType.objects.get_for_model(Review)
order_ct = ContentType.objects.get_for_model(Order)
orderitem_ct = ContentType.objects.get_for_model(OrderItem)

vendor_perms = Permission.objects.filter(content_type__in=[store_ct, product_ct])
vendors_group.permissions.set(vendor_perms)

buyer_perms = Permission.objects.filter(content_type__in=[review_ct, order_ct, orderitem_ct])
buyers_group.permissions.set(buyer_perms)

# Create test users
vendor = User.objects.create_user('vendor1', 'vendor@test.com', 'password123')
vendor.groups.add(vendors_group)

buyer = User.objects.create_user('buyer1', 'buyer@test.com', 'password123')
buyer.groups.add(buyers_group)

print("Setup complete!")
exit()
```

### Step 10: Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Test Accounts

- **Admin:** admin / admin123
- **Vendor:** vendor1 / password123
- **Buyer:** buyer1 / password123

## Project Structure
```
ecommerce_project/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── ecommerce_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── store/
    ├── migrations/
    ├── templates/
    ├── static/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

## Key URLs

- **Homepage:** `/`
- **Admin Panel:** `/admin/`
- **Vendor Dashboard:** `/vendor/dashboard/`
- **Buyer Dashboard:** `/buyer/dashboard/`
- **Browse Products:** `/products/`
- **Shopping Cart:** `/cart/`
- **Orders:** `/orders/`

## Development Notes

- Email backend is configured for console output in development
- For production, update `EMAIL_BACKEND` in settings.py
- Database uses MariaDB (production-ready)
- Sessions store shopping cart data

