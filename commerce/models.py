from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
import webcolors
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    age =  models.PositiveIntegerField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='assests/images/blog')

    def __str__(self): 
        return self.user.username



class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    descrition = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name =  'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name



class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,related_name='subcategory', null=True)
    name = models.CharField(max_length=250, unique=True)
    descrition = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name =  'Sub-Category'
        verbose_name_plural = 'Sub-Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    
    #product field information 
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # price information 
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    #inventory information 
    sku = models.CharField(max_length=10, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    dimension = models.CharField(max_length=10, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_sales = models.IntegerField(default=0) #how many times the product has been sold


    #ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    #for filtering and marking differnt section of frontend pages 
    is_featured = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_top = models.BooleanField(default=False)
    

    image = models.ImageField(upload_to='static/images/products')

     
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   validators=[MinValueValidator(1), MaxValueValidator(99)]
                                   )

    
    #date added 
    date_added = models.DateTimeField(auto_now_add=True)



    # def average_rating(self):
    #     'calculatee the average rating'
    #     reviews = self.reviews.all()
    #     if reviews.exists():
    #         return round(sum(reviews.rating for review in reviews) / reviews.count(), 1)
    #     return 0.0

    @property
    def get_discount_price_product(self):   
        if self.discount <= 0: 
            return ''
        elif self.discount >  100: 
            return {'error': 'discount cannot be greater than 100'}
        
        else:
            discount_cal =self.price *  (self.discount / 100)
            new_percentage_price = self.price - discount_cal
            return new_percentage_price
        
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ' '
        return url



   
    class Meta:
        ordering = ['-date_added']


    #helper function 
    # @property
    # def get_discount_percent(self):
    #     if self.old_price and self.old_price > self.price:
    #         discount = 100 * (self.old_price - self.price)/ self.old_price

    #         return round(discount, 0)
    #     return 0
    
    def __str__(self):
        return self.name
    

class Variation(models.Model):


    SIZE_CHOICE = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_type = models.CharField(max_length=6, null=True, blank=True, choices=SIZE_CHOICE)
    name = models.CharField(max_length=255)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    color_code = ColorField(null=True, blank=True, verbose_name='Color')


    def color_name(self):
        """Return a human-friendly color name for the HEX code."""
        if not self.color_code:
            return "Unknown"
        try:
            # Try exact CSS3 color match
            return webcolors.hex_to_name(self.color_code, spec='css3').title()
        except ValueError:
            # No exact match → find closest name
            return self._closest_color_name().title()

    
    def __str__(self):
        return f'{self.variation_type } - {self.name}'
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='reviews')
    customer = models.ForeignKey(Customer, models.SET_NULL, null=True)
    text = models.CharField(null=True, blank=True)
    email = models.EmailField()
    rating = models.PositiveIntegerField(default=0, 
            validators=[MinValueValidator(1), MaxValueValidator(5)]        
            )
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.product)
    class Meta:
        ordering = ['-created_at']


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    
    #use for guest cart, stoore the session key for indentifying cart from an authhenticated user or not
    session_key = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return str(self.customer)

    @property
    def get_cart_totals(self):
        cartitem = self.cartitem_set.all()
        total = sum(item.get_subtotal for item in cartitem)
        return total

    @property
    def get_total_quantity(self):
        cartitem = self.cartitem_set.all()
        total = sum(item.quantity for item in cartitem)
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    variation = models.ForeignKey(Variation, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def get_subtotal(self):
        total = self.product.price * self.quantity
        return total

  
    def __str__(self):
        return str(self.product)
    

class Order(models.Model):
    PENDING_STATUS = 'P'
    CANCELED_STATUS = 'C'
    DELIVERED_STATUS = 'D'

    ORDER_STATUS = [
        (PENDING_STATUS, 'Pending'), 
        (CANCELED_STATUS, 'Cancelled'), 
        (DELIVERED_STATUS, 'Delivered')
    ]

    customer = models.ForeignKey(Customer, models.CASCADE)
    description = models.TextField(null=True, blank=True)
    payment_status = models.CharField(5, choices=ORDER_STATUS, default=PENDING_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_type = models.CharField(max_length=255)
    transaction_id =  models.CharField(max_length=255)
    complete = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    
    @property
    def subtotal(self):
        orderitem = self.orderitem_set.all()
        total = sum([item.get_subtotal for item in orderitem])
        return total
    

    def __str__(self):
        return self.transaction_id

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return str( self.quantity)

    @property
    def get_subtotal(self):
        total = self.product.price * self.quantity
        return total

    
# building Shipiing feeas per state
class ShippingFee(models.Model):
    state = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return self.state 


class ShippingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    company_name = models.CharField(max_length=255, null=True)
    address = models.TextField(null=False)
    city = models.CharField(max_length=255, null=False)
    phone = models.IntegerField()
    email = models.EmailField()
    zipcode = models.CharField(max_length=255, null=False)
    date_added = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=255, null=True)



    def  __str__(self):
        return self.address

