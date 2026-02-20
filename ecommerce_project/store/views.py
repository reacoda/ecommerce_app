from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import timedelta
import secrets
from hashlib import sha256
from .models import Store, Product, Order, OrderItem, Review, PasswordResetToken

# Register user view


from django.contrib.auth.models import User, Group
from .forms import RegisterForm, LoginForm


def register_user(request):
    """
    Handle user registration with account type selection
    Uses Django Forms for proper validation
    """
    # If already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Get account type before saving
            account_type = form.cleaned_data.get("account_type")

            # Save user (but don't commit to DB yet)
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.save()

            # Assign user to correct group
            # Use get_or_create to avoid errors if group doesn't exist!
            if account_type == "vendor":
                group, created = Group.objects.get_or_create(name="Vendors")
                user.groups.add(group)
            elif account_type == "buyer":
                group, created = Group.objects.get_or_create(name="Buyers")
                user.groups.add(group)

            # Log the user in
            login(request, user)

            # Success message
            messages.success(
                request,
                f"Welcome {user.username}! Your {account_type} account has been created.",
            )

            # Redirect based on account type
            if account_type == "vendor":
                return redirect("store:vendor_dashboard")
            else:
                return redirect("store:buyer_dashboard")
        else:
            # Form has errors - show them to user
            messages.error(request, "Please fix the errors below")
    else:
        # GET request - show empty form
        form = RegisterForm()

    return render(request, "store/register.html", {"form": form})


# Login user view


def login_user(request):
    """
    Handle user login
    Uses Django's AuthenticationForm for proper validation
    """
    # If already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            # Get authenticated user from form
            user = form.get_user()

            # Log the user in
            login(request, user)

            # Save session data
            request.session["user_id"] = user.id
            request.session["username"] = user.username

            # Success message
            messages.success(request, f"Welcome back, {user.username}!")

            # Redirect based on group
            if user.groups.filter(name="Vendors").exists():
                return redirect("store:vendor_dashboard")
            elif user.groups.filter(name="Buyers").exists():
                return redirect("store:buyer_dashboard")
            else:
                return redirect("store:home")
        else:
            messages.error(request, "Invalid username or password")
    else:
        # GET request - show empty form
        form = LoginForm(request)

    return render(request, "store/login.html", {"form": form})


# Logout user view


def logout_user(request):
    """
    Handle user logout
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        msg = f"Goodbye, {username}! You have been logged out"
        messages.success(request, msg)

    return redirect("store:home")


# Password reset view


def password_reset_request(request):
    """
    Allow user to request password reset
    """
    if request.method == "POST":
        email = request.POST.get("email")

        # Validation
        if not email:
            messages.error(request, "Please enter your email address")
            return render(request, "store/password_reset_request.html")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            messages.success(
                request, "If that email exists, a reset link has been sent."
            )
            return redirect("store:login")

        # Generate secure token
        raw_token = secrets.token_urlsafe(32)
        hashed_token = sha256(raw_token.encode()).hexdigest()

        # Set expiration (5 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=5)

        # Create reset token
        reset_token = PasswordResetToken.objects.create(
            user=user, token=hashed_token, expires_at=expires_at
        )

        # Build reset URL
        reset_url = request.build_absolute_uri(
            reverse("store:password_reset_confirm",
                    kwargs={"token": raw_token})
        )

        # Send email
        from django.core.mail import EmailMessage

        subject = "Password Reset Request"
        body = f"""
Hello {user.username},

You requested a password reset for your account.

Click the link below to reset your password:
{reset_url}

This link will expire in 5 minutes.

If you didn't request this reset, please ignore this email.

Best regards,
The eCommerce Team
        """

        email_message = EmailMessage(
            subject, body, "noreply@ecommerce.com", [user.email]
        )

        try:
            email_message.send()
            print(f"Password reset email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

        messages.success(request,
                         "If that email exists, a reset link has been sent.")
        return redirect("store:login")

    else:
        return render(request, "store/password_reset_request.html")


def password_reset_confirm(request, token):
    """
    Confirm password reset with token
    """
    # Hash the token from URL
    hashed_token = sha256(token.encode()).hexdigest()

    # Find the reset token
    try:
        reset_token = PasswordResetToken.objects.get(token=hashed_token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid or expired reset link")
        return redirect("store:login")

    # Check if token is valid
    if not reset_token.is_valid():
        messages.error(request, "This reset link has expired or been used")
        return redirect("store:password_reset_request")

    if request.method == "POST":
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        # Validation
        if not password or not password_confirm:
            messages.error(request, "Both password fields are required")
            return render(
                request, "store/password_reset_confirm.html", {"token": token}
            )

        if password != password_confirm:
            messages.error(request, "Passwords do not match")
            return render(
                request, "store/password_reset_confirm.html", {"token": token}
            )

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(
                request, "store/password_reset_confirm.html", {"token": token}
            )

        # Reset the password
        user = reset_token.user
        user.set_password(password)
        user.save()

        # Mark token as used
        reset_token.used = True
        reset_token.save()

        messages.success(request,
                         "Password reset successfully! You can now login.")
        return redirect("store:login")

    else:
        return render(request,
                      "store/password_reset_confirm.html", {"token": token})


# Homepage view


def home(request):
    """Homepage view"""
    return render(request, "store/home.html")


@login_required(login_url="store:login")
def vendor_dashboard(request):
    """
    Vendor dashboard - placeholder for now
    """
    return render(request, "store/vendor/dashboard.html")


@login_required(login_url="store:login")
def buyer_dashboard(request):
    """
    Buyer dashboard - placeholder for now
    """
    return render(request, "store/buyer/dashboard.html")


# Create Store View


@login_required(login_url="store:login")
def vendor_store_create(request):
    """
    Allow vendors to create a new store
    """
    # Check user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can create stores")
        return redirect("store:home")

    # Get data from form
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        # validation
        # Check if the field are empty
        if not name or not description:
            messages.error(request, "Name and description are required")
            return render(request, "store/vendor/store_create.html")

        # Check if store name already exists for this vendor

        if Store.objects.filter(owner=request.user, name=name).exists():
            messages.error(request, "Store already exists")
            return render(request, "store/vendor/store_create.html")

        # Create the store
        store = Store.objects.create(
            name=name,
            description=description,
            owner=request.user,  # Current logged-in user
        )

        # Success message and redirect
        messages.success(request, f'Store "{store.name}" created successfully')

        return redirect("store:vendor_stores_list")

    else:
        return render(request, "store/vendor/store_create.html")


# Vendor Store List View

# Check if user is logged in


@login_required(login_url="store:login")
def vendor_stores_list(request):
    """Show all stores owned by current vendor"""

    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can view their stores")
        return redirect("store:home")

    # Get all stores where owner = current user
    stores = Store.objects.filter(owner=request.user)

    # Pass stores to template
    context = {"stores": stores}
    return render(request, "store/vendor/stores_list.html", context)


# Vendor Store Create View


@login_required(login_url="store:login")
def vendor_product_add(request, store_pk):
    """
    Allow vendors to add a product to their store

    Args:
        store_pk: The ID of the store to add product to
    """
    # Check if the user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can add products")
        return redirect("store:home")

    # Get the store by store_pk
    store = get_object_or_404(Store, pk=store_pk)

    # Check if current user owns this store
    if store.owner != request.user:
        messages.error(request, "You can only add products to your own stores")
        return redirect("store:vendor_stores_list")

    # Get data from form
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        # Validation
        # Check if fields are empty
        if not name or not description or not price or not stock:
            messages.error(request, "All fields are required")
            return render(request, "store/vendor/product_add.html")

        # Check if price is valid (greater than 0)
        try:
            price = float(price)
            if price <= 0:
                messages.error(request, "Price must be greater than 0")
                return render(
                    request, "store/vendor/product_add.html", {"store": store}
                )
        except ValueError:
            messages.error(request, "Price must be a valid number")
            return render(request,
                          "store/vendor/product_add.html", {"store": store})

        # Check if stock is valid (not negative)
        try:
            stock = int(stock)
            if stock < 0:
                messages.error(request, "Stock cannot be negative")
                return render(
                    request, "store/vendor/product_add.html", {"store": store}
                )
        except ValueError:
            messages.error(request, "Stock must be a valid number")
            return render(request,
                          "store/vendor/product_add.html", {"store": store})

        # Create the product
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            store=store
        )

        # Success message and redirect
        messages.success(request,
                         f'Product "{product.name}" added successfully!')
        return redirect("store:vendor_products_list")

    else:
        # Pass store to template and show form
        return render(request, 
                      "store/vendor/product_add.html", {"store": store})


# Store Detail View
# Check if user is logged in


@login_required(login_url="store:login")
def vendor_store_detail(request, pk):
    """
    Show store details with all products in that store

    Args:
        pk: The ID of the store
    """
    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can add products")
        return redirect("store:home")

    # Get the store by pk
    store = get_object_or_404(Store, pk=pk)

    # Check if current user owns this store
    if store.owner != request.user:
        messages.error(request, "You can only view your own store details")
        return redirect("store:vendor_stores_list")

    # Get all products in this store
    products = Product.objects.filter(store=store)

    # Pass both store and products to template
    context = {"store": store, "products": products}

    return render(request, "store/vendor/store_detail.html", context)


# Edit Store View
# Check if user is logged-in


@login_required(login_url="store:login")
def vendor_store_edit(request, pk):
    """
    Allow vendors to edit their store

    Args:
        pk: The ID of the store to edit
    """
    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can add products")
        return redirect("store:home")

    # Get the store by pk
    store = get_object_or_404(Store, pk=pk)

    # Check if the current user owns the store
    if store.owner != request.user:
        messages.error(request, "You can only edit your own store")
        return redirect("store:vendor_stores_list")

    # Get data from form
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")

        # Validation
        if not name or not description:
            messages.error(request, "Name and description are required")
            return render(request, "store/vendor/store_edit.html")

        # Check if store name already exists (excluding current store)
        if Store.objects.filter(
            owner=request.user, name=name
             ).exclude(pk=pk).exists():
            messages.error(request, "You already have a store with this name")
            return render(request,
                          "store/vendor/store_edit.html", {"store": store})

        # Update the store (don't create new)
        store.name = name
        store.description = description
        store.save()

        # Success message and redirect
        messages.success(request,
                         f'Store "{store.name}" updated successfully!')
        return redirect("store:vendor_store_detail", pk=store.pk)

    else:
        # Show form with current store data
        return render(request,
                      "store/vendor/store_edit.html", {"store": store})


# Delete Store View
# Check if the current user is logged-in


@login_required(login_url="store:login")
def vendor_store_delete(request, pk):
    """
    Allow vendors to delete their store(only if it has no products)

    Args:
        pk: The ID of the store to delete
    """
    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can add products")
        return redirect("store:home")

    # Get the store by pk
    store = get_object_or_404(Store, pk=pk)

    # Check if the current user owns the store
    if store.owner != request.user:
        messages.error(request, "You can only delete your own store")
        return redirect("store:vendor_stores_list")

    # Check if store has products
    product_count = Product.objects.filter(store=store).count()

    if product_count > 0:
        messages.error(
            request,
            f"Cannot delete store with \
            {product_count} products. Delete products first",
        )
        return redirect("store:vendor_store_detail", pk=store.pk)

    # Save store name for message
    store_name = store.name

    # Delete the store
    store.delete()

    # Success message and redirect
    messages.success(request, f'Store "{store_name}" deleted successfully!')
    return redirect("store:vendor_stores_list")


# Products List View


@login_required(login_url="store:login")
def vendor_products_list(request):
    """
    Show all products from all stores owned by current vendor
    """
    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can view products")
        return redirect("store:home")

    # Get all products where the store owner is current user
    products = Product.objects.filter(store__owner=request.user)

    # Pass to template
    context = {"products": products}
    return render(request, "store/vendor/products_list.html", context)


# Product edit view

# make sure that the user is logged in


@login_required(login_url="store:login")
def vendor_product_edit(request, pk):
    """
    Allow vendors to edit their product

    Args:
        pk: The ID of the product to edit
    """
    # Check if user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can edit products")
        return redirect("store:home")

    # Get the product by pk
    product = get_object_or_404(Product, pk=pk)

    # Check if current user owns the store
    if product.store.owner != request.user:
        messages.error(request, "You can only edit your own products")
        return redirect("store:vendor_products_list")

    if request.method == "POST":
        # Get data from form
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        # Validation
        # Check if all fields are provided
        if not name or not description or not price or not stock:
            messages.error(request, "All fields are required")
            return render(
                request, "store/vendor/product_edit.html", {"product": product}
            )

        # Check if price is valid (greater than 0)
        try:
            price = float(price)
            if price <= 0:
                messages.error(request, "Price must be greater than 0")
                return render(
                    request,
                    "store/vendor/product_edit.html", {"product": product}
                )
        except ValueError:
            messages.error(request, "Price must be a valid number")
            return render(
                request, "store/vendor/product_edit.html", {"product": product}
            )

        # Check if stock is valid (not negative)
        try:
            stock = int(stock)
            if stock < 0:
                messages.error(request, "Stock cannot be negative")
                return render(
                    request,
                    "store/vendor/product_edit.html",
                    {"product": product}
                )
        except ValueError:
            messages.error(request, "Stock must be a valid number")
            return render(
                request, "store/vendor/product_edit.html", {"product": product}
            )

        # Update the product
        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.save()  # Save changes to database

        # Success message and redirect
        messages.success(request,
                         f'Product "{product.name}" updated successfully!')
        return redirect("store:vendor_products_list")

    else:
        # GET request - show form with current product data
        return render(request,
                      "store/vendor/product_edit.html", {"product": product})


# Product Delete View


@login_required(login_url="store:login")
def vendor_product_delete(request, pk):
    """
    Allow vendors to delete their product

    Args:
        pk: The ID of the product to delete
    """
    # Check if the user is a vendor
    if not request.user.groups.filter(name="Vendors").exists():
        messages.error(request, "Only vendors can edit products")
        return redirect("store:home")

    # Get the product by pk
    product = get_object_or_404(Product, pk=pk)

    # Check if the current user owns the store
    if product.store.owner != request.user:
        messages.error(request, "You can only delete your own products")
        return redirect("store:vendor_products_list")

    # Save product name for message (before deleting!)
    product_name = product.name

    # Delete the product
    product.delete()

    # Success message and redirect
    messages.success(request,
                     f'Product "{product_name}" deleted successfully!')
    return redirect("store:vendor_products_list")


# ===== BUYER SHOPPING VIEWS =====


def products_browse(request):
    """
    Show all products from all stores for buyers to browse
    Anyone can view (no login required)
    """
    # Get all products
    products = Product.objects.all().order_by("-created_at")

    # Pass to template
    context = {"products": products}
    return render(request, "store/buyer/products_browse.html", context)


def product_detail(request, pk):
    """
    Show detailed information about a specific product
    Anyone can view all the products
    """
    # Get product by pk
    product = get_object_or_404(Product, pk=pk)

    # Get all reviews for this product
    reviews = Review.objects.filter(product=product).order_by("-created_at")

    # Check if user has bought this product
    can_review = False
    already_reviewed = False

    if request.user.is_authenticated:
        # Check if already reviewed
        already_reviewed = Review.objects.filter(
            buyer=request.user, product=product
        ).exists()

        # Check if user has purchased this product
        has_purchased = OrderItem.objects.filter(
            order__buyer=request.user, product=product
        ).exists()

        can_review = has_purchased

    # Pass to template
    context = {
        "product": product,
        "reviews": reviews,
        "can_review": can_review,
        "already_reviewed": already_reviewed,  # ← Add this!
    }
    return render(request, "store/buyer/product_detail.html", context)


# ===== BUYER CART VIEWS =====


@login_required(login_url="store:login")
def cart_add(request, product_pk):
    """
    Add a product to the shopping cart (stored in session)
    """
    # Get the product
    product = get_object_or_404(Product, pk=product_pk)

    # Get quantity from POST (default to 1)
    quantity = int(request.POST.get("quantity", 1))

    # Ensure quantity is at least 1
    if quantity < 1:
        quantity = 1

    # Check if enough stock
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} units available")
        return redirect("store:product_detail", pk=product_pk)

    # Get cart from session (or create empty dict)
    cart = request.session.get("cart", {})

    # Product ID as string (session keys must be strings)
    product_id = str(product_pk)

    # Add or update quantity in cart
    if product_id in cart:
        # Check total quantity doesn't exceed stock
        new_quantity = cart[product_id] + quantity
        if new_quantity > product.stock:
            messages.error(
                request,
                f"Cannot add more. Only {product.stock} units available"
            )
            return redirect("store:product_detail", pk=product_pk)
        cart[product_id] = new_quantity
    else:
        cart[product_id] = quantity

    # Save cart back to session
    request.session["cart"] = cart
    request.session.modified = True  # Tell Django to save the session

    # Success message
    messages.success(request, f"Added {product.name} to cart")

    # Redirect to products browse
    return redirect("store:products_browse")


@login_required(login_url="store:login")
def cart_view(request):
    """
    Display the shopping cart with all items
    """
    # Get cart from session
    cart = request.session.get("cart", {})

    # Build list of cart items with product details
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id))
            subtotal = product.price * quantity
            total_price += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
        except Product.DoesNotExist:
            # Product was deleted, remove from cart
            pass

    # Pass to template
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_count": len(cart_items),
    }
    return render(request, "store/buyer/cart.html", context)


@login_required(login_url="store:login")
def cart_update(request, product_pk):
    """
    Update the quantity of a product in the cart
    """
    if request.method == "POST":
        # Get new quantity
        quantity = int(request.POST.get("quantity", 1))

        # Get product to check stock
        product = get_object_or_404(Product, pk=product_pk)

        # Validate quantity
        if quantity < 1:
            messages.error(request, "Quantity must be at least 1")
            return redirect("store:cart_view")

        if quantity > product.stock:
            messages.error(request, f"Only {product.stock} units available")
            return redirect("store:cart_view")

        # Update cart
        cart = request.session.get("cart", {})
        product_id = str(product_pk)

        if product_id in cart:
            cart[product_id] = quantity
            request.session["cart"] = cart
            request.session.modified = True
            messages.success(request, f"Updated {product.name} quantity")

    return redirect("store:cart_view")


@login_required(login_url="store:login")
def cart_remove(request, product_pk):
    """
    Remove a product from the cart
    """
    # Get cart
    cart = request.session.get("cart", {})
    product_id = str(product_pk)

    # Remove product if it exists
    if product_id in cart:
        # Get product name for message
        try:
            product = Product.objects.get(pk=product_pk)
            product_name = product.name
        except Product.DoesNotExist:
            product_name = "Product"

        del cart[product_id]
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, f"Removed {product_name} from cart")

    return redirect("store:cart_view")


@login_required(login_url="store:login")
def cart_clear(request):
    """
    Clear all items from the cart
    """
    request.session["cart"] = {}
    request.session.modified = True
    messages.success(request, "Cart cleared")
    return redirect("store:cart_view")


# ===== BUYER CHECKOUT & ORDERS =====


@login_required(login_url="store:login")
def checkout(request):
    """
    Process checkout: create order, order items, send email
    """
    # Check if user is a buyer
    if not request.user.groups.filter(name="Buyers").exists():
        messages.error(request, "Only buyers can checkout")
        return redirect("store:home")

    # Get cart from session
    cart = request.session.get("cart", {})

    # Check if cart is empty
    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect("store:products_browse")

    # Calculate total and validate stock
    total_price = 0
    cart_items = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id))

            # Check stock availability
            if quantity > product.stock:
                messages.error(
                    request,
                    f"Not enough stock for {product.name}. \
                    Only {product.stock} available",
                )
                return redirect("store:cart_view")

            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
        except Product.DoesNotExist:
            messages.error(request,
                           "Some products in your cart no longer exist")
            return redirect("store:cart_view")

    # Create the order
    order = Order.objects.create(buyer=request.user, total_price=total_price)

    # Create order items and update stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            price=item["product"].price,  # Save price at time of purchase
        )

        # Reduce product stock
        product = item["product"]
        product.stock -= item["quantity"]
        product.save()

    # Clear cart
    request.session["cart"] = {}
    request.session.modified = True

    # ===== SEND INVOICE EMAIL =====

    # Build invoice email
    subject = f"Order Confirmation - Order #{order.id}"

    body = f"""
    Dear {request.user.username},

    Thank you for your order! Your order has been confirmed.

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ORDER DETAILS
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Order Number: #{order.id}
    Order Date: {order.order_date.strftime('%B %d, %Y at %H:%M')}

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ITEMS ORDERED
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    """

    # Add each item
    for item in cart_items:
        body += f"""
    Product: {item['product'].name}
    Store: {item['product'].store.name}
    Quantity: {item['quantity']}
    Price: R{item['product'].price} each
    Subtotal: R{item['subtotal']}
    ─────────────────────────────────────────
    """

    body += f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TOTAL: R{total_price}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Thank you for shopping with us!

    If you have any questions about your order, please contact us.

    Best regards,
    The eCommerce Team
    """

    # Create and send email
    email = EmailMessage(
        subject,
        body,
        "noreply@ecommerce.com",  # From email
        [request.user.email],  # To email
    )

    try:
        email.send()
        print(f" Invoice email sent to {request.user.email}")
    except Exception as e:
        print(f" Failed to send email: {e}")
        # Don't fail the checkout if email fails

    # Success message
    messages.success(
        request, f"Order #{order.id} placed successfully!"
                 f"Check your email for invoice."
    )

    # Redirect to order detail
    return redirect("store:order_detail", pk=order.pk)


@login_required(login_url="store:login")
def order_history(request):
    """
    Show all orders for the current buyer
    """
    # Check if user is a buyer
    if not request.user.groups.filter(name="Buyers").exists():
        messages.error(request, "Only buyers can view order history")
        return redirect("store:home")

    # Get all orders for this buyer
    orders = Order.objects.filter(buyer=request.user).order_by("-order_date")

    # Pass to template
    context = {"orders": orders}
    return render(request, "store/buyer/order_history.html", context)


@login_required(login_url="store:login")
def order_detail(request, pk):
    """
    Show details of a specific order
    """
    # Get the order
    order = get_object_or_404(Order, pk=pk)

    # Check if current user owns this order
    if order.buyer != request.user:
        messages.error(request, "You can only view your own orders")
        return redirect("store:order_history")

    # Get all items in this order with review status
    order_items = OrderItem.objects.filter(order=order)

    # Add review status to each item
    items_with_review_status = []
    for item in order_items:
        # Check if user has reviewed this product
        has_reviewed = Review.objects.filter(
            buyer=request.user, product=item.product
        ).exists()

        items_with_review_status.append(
            {"order_item": item, "has_reviewed": has_reviewed}
        )

    # Pass to template
    context = {"order": order,
               "order_items_with_status": items_with_review_status}
    return render(request, "store/buyer/order_detail.html", context)


# ===== REVIEWS =====


@login_required(login_url="store:login")
def review_add(request, product_pk):
    """
    Allow buyers to add a review for a product.
    - Verified review: buyer has purchased the product
    - Unverified review: buyer has NOT purchased the product
    Both are allowed but marked differently!
    """
    # Check if user is a buyer
    if not request.user.groups.filter(name="Buyers").exists():
        messages.error(request, "Only buyers can leave reviews")
        return redirect("store:home")

    # Get the product
    product = get_object_or_404(Product, pk=product_pk)

    # Check if user already reviewed this product
    existing_review = Review.objects.filter(
        buyer=request.user, product=product
    ).exists()

    if existing_review:
        messages.error(request, "You have already reviewed this product")
        return redirect("store:product_detail", pk=product_pk)

    if request.method == "POST":
        # Get review data
        content = request.POST.get("content")
        rating = request.POST.get("rating")

        # Validation
        if not content or not rating:
            messages.error(request,
                           "Please provide both rating and review text")
            return redirect("store:product_detail", pk=product_pk)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, "Rating must be between 1 and 5")
                return redirect("store:product_detail", pk=product_pk)
        except ValueError:
            messages.error(request, "Invalid rating value")
            return redirect("store:product_detail", pk=product_pk)

        # Check if user purchased this product
        # This determines if review is verified or unverified
        has_purchased = OrderItem.objects.filter(
            order__buyer=request.user, product=product
        ).exists()

        # Create review
        # verified=True if purchased, verified=False if not purchased
        # BOTH are allowed! Just marked differently
        review = Review.objects.create(
            product=product,
            buyer=request.user,
            content=content,
            rating=rating,
            verified=has_purchased,  # True if bought, False if not
        )

        # Show different messages based on verification
        if has_purchased:
            messages.success(
                request, "Verified review added! (You purchased this product)"
            )
        else:
            messages.success(
                request,
                "Unverified review added! "
                "(Purchase this product to get a verified badge)",
            )

        return redirect("store:product_detail", pk=product_pk)

    # If GET request redirect to product detail
    return redirect("store:product_detail", pk=product_pk)


# Test URL View
def test_urls(request):
    """Debug view to test URL resolution"""
    # from django.urls import reverse

    urls = {
        "home": reverse("store:home"),
        "register": reverse("store:register"),
        "login": reverse("store:login"),
        "vendor_dashboard": reverse("store:vendor_dashboard"),
        "vendor_store_create": reverse("store:vendor_store_create"),
        "vendor_stores_list": reverse("store:vendor_stores_list"),
    }

    return render(request, "store/test_urls.html", {"urls": urls})
