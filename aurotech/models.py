from django.db import models # type: ignore

from django.urls import reverse # type: ignore
from cloudinary.models import CloudinaryField




class CoreProduct(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    core_product = models.ForeignKey(
        CoreProduct,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    filter_size = models.CharField(max_length=100, blank=True, null=True)
    pore_size = models.CharField(max_length=100, blank=True, null=True)
    diameter = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    image = CloudinaryField('image')
    odoo_id = models.IntegerField(null=True, blank=True, help_text="ID of this product in Odoo")
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def __str__(self):
        return self.name



class QuoteRequest(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.product.name}"