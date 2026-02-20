from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Store(models.Model):
    """
    Model representing store

    Fields:
        name: (CharField) - name of the store (max 200 characters)
        description: (TextField) - description of the store (can be long text)
        owner: (ForeignKey - User) - Owner of the store
        created_at: (DateTimeField) - when the store was created
    """

    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the store name when the object is printed"""
        return self.name

    class Meta:
        # newest store first
        ordering = ["-created_at"]


class Product(models.Model):
    """
    Model representing product in a store

    Fields:
        name: (CharField, max 200, required) - name of the product
        description: (TextField, required) - description of the product
        price: (DecimalField, max 10 digits, 2 decimal places) -
        price of the product.
        stock: (PositiveIntegerField) - the quantity of the product
        store: (ForeignKey to Store, cascade delete) the store which the
        product belongs to
        created_at: (DateTimeField, auto-filled) - when the product was created
    """

    name = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # ForeignKey to store. If store is deleted, all its products are deleted
    #  too
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the product name when the object is printed"""
        return self.name

    class Meta:
        # newest product first
        ordering = ["-created_at"]


class Review(models.Model):
    """
    Model representing a product review

    Fields:
        content: (TextField, required) - the review text
        rating: (IntegerField, choices 1-5) - star rating
        product: (ForeignKey to Product, cascade)
        buyer: (ForeignKey to User, cascade)
        verified: (Boolean, default False) - Did they buy it
        created_at: (DateTimeField, auto)
    """

    content = models.TextField(blank=False, null=False)
    # This ensures that rating is only 1, 2, 3, 4, 5
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return review by {buyer} for {product}"""
        return f"Review by {self.buyer.username} for {self.product.name}"

    class Meta:
        # newest review first
        ordering = ["-created_at"]


class Order(models.Model):
    """
    Model representing a customer order

    Fields:
        buyer: (ForeignKey to User, cascade) - the buyer of the product
        order_date (DateTimeField, auto) - when the order was made
        total_price (DecimalField, max 10 digits, 2 decimals) - total price of
        the order
    """

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Return order number by buyer"""
        return f"Order #{self.id} by {self.buyer.username}"

    class Meta:
        # newest order first
        ordering = ["-order_date"]


class OrderItem(models.Model):
    """
    Model representing individual items in an order
    (connects Order to Products with quantity and price)

    Fields:
        order: (ForeignKey to Order, cascade) - the order that was made
        product: (ForeignKey to Product, cascade) - the product in the order
        quantity: (PositiveIntegerField) - the amount of product ordered
        price: (DecimalField, max 10 digits, 2 decimals) - the price
        at time of purchase
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # default to 1
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Return {quantity}x {product} in Order #{order.id}"""
        return f"{self.quantity}x {self.product.name} \
        in Order #{self.order.id}"

    class Meta:
        # order by order, then product name
        ordering = ["order", "product__name"]


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens

    Fields:
        user: User who requested reset
        token: Hashed token for security
        created_at: When token was created
        expires_at: When token expires
        used: Whether token has been used
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.username}"

    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        from django.utils import timezone

        return not self.used and timezone.now() < self.expires_at

    class Meta:
        ordering = ["-created_at"]
