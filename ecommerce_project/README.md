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
cd path/to/ecommerce_app/ecommerce_project
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
```bash
cp .env.example .env
```

4. **Edit `.env`** with your database credentials

### Step 6: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 8: Create Groups & Test Users
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

### Step 9: Run Development Server
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

