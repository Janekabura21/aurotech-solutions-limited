

# Create your views here.
from django.shortcuts import get_object_or_404, render

from AuroTech.models import CoreProduct, Product





# Homepage view (shows core products)
def home(request):
    return render(request, 'AuroTech/home.html')

# Core Product Detail (shows all products under it)
def core_product_detail(request, slug):
    core_product = get_object_or_404(CoreProduct, slug=slug)
    products = core_product.products.all()  # all products under this core product
    return render(request, 'AuroTech/core_product_detail.html', {
        'core_product': core_product,
        'products': products
    })

# Individual Product Detail (optional)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'AuroTech/product_detail.html', {
        'product': product
    })

def product_full_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'AuroTech/product.html', {
        'product': product
    })