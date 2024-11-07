from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


User = get_user_model()


class UserRegister(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_store_owner = models.BooleanField(default=False)
    store_name = models.CharField(max_length=255, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='ev_users',  # Change related_name to avoid conflicts
        blank=True,
        help_text=('The groups this user belongs to.\
            A user will get all permissions granted to each of their groups.'),
        related_query_name='ev_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='ev_users',  # Change related_name to avoid conflicts
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='ev_user',
    )


class EVItem(models.Model):
    cutoff = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    old_price = models.CharField(max_length=50, blank=True, null=True)
    new_price = models.CharField(max_length=50, blank=True, null=True)
    banner = models.CharField(max_length=255, blank=True, null=True)
    display_photo = models.CharField(max_length=255, blank=True, null=True)
    menu = models.CharField(max_length=255, blank=True, null=True)
    star = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title


class EVCategory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    items = models.ManyToManyField(EVItem, related_name='categories')

    def __str__(self):
        return self.name


class EVStore(models.Model):
    cutoff = models.CharField(max_length=255, blank=True, null=True)
    item = models.CharField(max_length=255, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    rating = models.CharField(max_length=10, blank=True, null=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    banner = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    delivery_time = models.CharField(max_length=50, blank=True, null=True)
    delivery_fee = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    category = models.ManyToManyField(
        EVCategory, related_name='stores', blank=True
    )
    # category = models.ForeignKey(
    # EVCategory, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class EVSuperCategory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    store = models.ManyToManyField(EVStore, related_name='super', blank=True)
    # store = models.ForeignKey(
    # EVStore, null=True,
    # blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class EVItemCart(models.Model):
    thumbnail = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    new_price = models.CharField(max_length=50)
    star = models.CharField(max_length=255)

    def __str__(self):
        return self.title

  
class EVOrderItem(models.Model):
    # itemOrder = models.ManyToManyField(EVItem, related_name='order')
    itemOrder = models.ManyToManyField(EVItemCart, related_name="orders")
    quantity = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class EVShippingAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.address


class EVOrder(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    orders = models.ManyToManyField(EVOrderItem, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    shippingAddress = models.OneToOneField(
        EVShippingAddress, on_delete=models.CASCADE,
        related_name='shipping_address')

    def __str__(self):
        return self.status
