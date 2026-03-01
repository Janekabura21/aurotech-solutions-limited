

# Create your views here.
from django.shortcuts import get_object_or_404, render # type: ignore
from django.db.models import Q
from AuroTech.models import CoreProduct, Product
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        full_message = f"""
Name: {name}
Email: {email}

Message:
{message_text}
"""

        send_mail(
            subject=f"New Contact Form Submission from {name}",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # redirect to same page to clear POST

    return render(request, 'AuroTech/contact.html')



# Homepage view (shows core products)
def home(request):
    core_products = CoreProduct.objects.all()
    return render(request, 'AuroTech/home.html', {
        'core_products': core_products
    })


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

def all_products(request):
    products = Product.objects.all()  # fetch all products
    return render(request, 'AuroTech/all_products.html', {'products': products})


def search_products(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'AuroTech/search_results.html', {
        'query': query,
        'results': results
    })

def about_us(request):
    return render(request, 'AuroTech/about_us.html')