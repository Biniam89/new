from django.db import models
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=200)
    country_of_origin = models.CharField(max_length=100, blank=True)
    def __str__(self): return self.name

class Phone(models.Model):
    title = models.CharField(max_length=255)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='phones/', blank=True, null=True)
    
    storage_capacity = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 256GB")
    ram = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 8GB")
    screen_size = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 6.1 inches")
    battery = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 4000 mAh")
    
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0, help_text="Number of items in stock")

    def __str__(self):
        return f"{self.brand.name if self.brand else ''} {self.title}"

    @property
    def average_rating(self):
        comments = self.comments.all()
        if comments.exists():
            return round(sum(c.rating for c in comments) / comments.count(), 1)
        return 0

    @property
    def stars_html(self):
        rating = self.average_rating
        full = int(rating)
        half = 1 if (rating - full) >= 0.5 else 0
        empty = 5 - full - half
        
        html = '<i class="bi bi-star-fill text-warning"></i> ' * full
        if half:
            html += '<i class="bi bi-star-half text-warning"></i> '
        html += '<i class="bi bi-star text-warning"></i> ' * empty
        return html
class PhoneImage(models.Model):
    phone = models.ForeignKey(Phone, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='phones/gallery/')

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
    def __str__(self): return self.user.username

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self): return f"Order {self.id} by {self.customer.user.username}"

class Comment(models.Model):
    phone = models.ForeignKey(Phone, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    body = models.TextField()
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], default=5)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.phone.title}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_cart_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.phone.price * self.quantity