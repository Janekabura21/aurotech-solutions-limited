from django.db import models

from django.urls import reverse


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
    
    image = models.ImageField(upload_to='products/')

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def __str__(self):
        return self.name
