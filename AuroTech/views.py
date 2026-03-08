

# Create your views here.
from django.shortcuts import get_object_or_404, render # type: ignore
from django.db.models import Q
from aurotech.models import CoreProduct, QuoteRequest, Product
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

    return render(request, 'aurotech/contact.html')



# Homepage view (shows core products)
def home(request):
    core_products = CoreProduct.objects.all()
    return render(request, 'aurotech/index.html', {
        'core_products': core_products
    })


# Core Product Detail (shows all products under it)
def core_product_detail(request, slug):
    core_product = get_object_or_404(CoreProduct, slug=slug)
    products = core_product.products.all()  # all products under this core product
    return render(request, 'aurotech/core_product_detail.html', {
        'core_product': core_product,
        'products': products
    })

# Individual Product Detail (optional)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'aurotech/product_detail.html', {
        'product': product
    })

def all_products(request):
    products = Product.objects.all()  # fetch all products
    return render(request, 'aurotech/all_products.html', {'products': products})

def services(request):
    return render(request, "aurotech/services.html")


def search_products(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'aurotech/search_results.html', {
        'query': query,
        'results': results
    })

def about_us(request):
    return render(request, 'aurotech/about_us.html')







from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, QuoteRequest
import requests
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, QuoteRequest
import requests

# Odoo Configuration
ODOO_URL = "https://aurotech-solutions-limited1.odoo.com/"
API_KEY = "91a353fe1a8986860ad67931757a811304ee0477"
DB = "aurotech-solutions-limited1"
USER_ID = 2  # Odoo admin user ID

# Helper functions
def create_or_get_partner(name, email, company, phone):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    # Check if partner exists
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB, USER_ID, API_KEY,
                "res.partner", "search_read",
                [[["email", "=", email]]],
                {"fields": ["id", "name"]}
            ]
        },
        "id": 1
    }
    try:
        response = requests.post(f"{ODOO_URL}/jsonrpc", headers=headers, json=payload).json()
        if response.get("result"):
            return response["result"][0]["id"]
    except Exception as e:
        print("Error checking partner:", e)

    # Create partner if not exists
    payload_create = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB, USER_ID, API_KEY,
                "res.partner", "create",
                [{"name": name, "email": email, "company_type": "company" if company else "person", "phone": phone}]
            ]
        },
        "id": 2
    }
    try:
        response_create = requests.post(f"{ODOO_URL}/jsonrpc", headers=headers, json=payload_create).json()
        return response_create.get("result")
    except Exception as e:
        print("Error creating partner:", e)
        return None

def create_sale_order_multi(partner_id, order_lines, message):
    if not order_lines:
        return None
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB, USER_ID, API_KEY,
                "sale.order", "create",
                [{"partner_id": partner_id, "note": message, "order_line": order_lines}]
            ]
        },
        "id": 3
    }
    try:
        response = requests.post(f"{ODOO_URL}/jsonrpc", headers=headers, json=payload).json()
        return response.get("result")
    except Exception as e:
        print("Error creating sale order:", e)
        return None

# Main view
def request_multi_quote(request):
    products = Product.objects.all()

    if request.method == "POST":
        name = request.POST.get("name") or ""
        company = request.POST.get("company") or ""
        email = request.POST.get("email") or ""
        phone = request.POST.get("phone") or ""
        message = request.POST.get("message") or ""

        order_lines = []
        email_lines = ""
        selected_any = False

        for product in products:
            try:
                qty = int(request.POST.get(f"quantity_{product.id}") or 0)
            except ValueError:
                qty = 0

            if qty > 0:
                selected_any = True

                if not product.odoo_id:
                    print(f"Skipping product {product.name} – missing Odoo ID")
                    continue

                order_lines.append((0, 0, {"product_id": product.odoo_id, "product_uom_qty": qty}))

                # Save in Django DB
                QuoteRequest.objects.create(
                    product=product,
                    name=name,
                    company=company,
                    email=email,
                    phone=phone,
                    quantity=qty,
                    message=message
                )

                email_lines += f"{product.name} - Quantity: {qty}\n"

        if not selected_any:
            messages.error(request, "Please select at least one product.")
            return render(request, "aurotech/request_multi_quote.html", {"products": products})

        # Send email
        try:
            subject = "New Multi-Product Quote Request"
            email_message = f"""
New Multi-Product Quote Request Received

Name: {name}
Company: {company}
Email: {email}
Phone: {phone}

Products:
{email_lines}

Message:
{message}
"""
            send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, ["aurotechltd@gmail.com"], fail_silently=False)
        except Exception as e:
            print("Email sending error:", e)

        # Integrate with Odoo
        try:
            partner_id = create_or_get_partner(name, email, company, phone)
            if partner_id:
                sale_order_id = create_sale_order_multi(partner_id, order_lines, message)
                print("Created Odoo sale order ID:", sale_order_id)
            else:
                print("Partner creation failed – sale order not created")
        except Exception as e:
            print("Odoo integration error:", e)

        messages.success(request, "Your quote request has been submitted successfully.")
        return render(request, "aurotech/quote_success.html", {"products": products})

    return render(request, "aurotech/request_multi_quote.html", {"products": products})













# def request_quote(request, slug):
#     product = get_object_or_404(Product, slug=slug)

#     if request.method == "POST":
#         # -------------------------------
#         # Get form data safely
#         # -------------------------------
#         name = request.POST.get("name") or ""
#         company = request.POST.get("company") or ""
#         email = request.POST.get("email") or ""
#         phone = request.POST.get("phone") or ""
#         quantity = int(request.POST.get("quantity") or 1)
#         message = request.POST.get("message") or ""

#         # -------------------------------
#         # Save in Django DB
#         # -------------------------------
#         QuoteRequest.objects.create(
#             product=product,
#             name=name,
#             company=company,
#             email=email,
#             phone=phone,
#             quantity=quantity,
#             message=message
#         )

#         # -------------------------------
#         # Send email to business
#         # -------------------------------
#         subject = f"New Quote Request - {product.name}"

#         email_message = f"""
# New Quote Request Received

# Product: {product.name}
# Name: {name}
# Company: {company}
# Email: {email}
# Phone: {phone}
# Quantity: {quantity}

# Message:
# {message}
# """

#         send_mail(
#             subject,
#             email_message,
#             settings.DEFAULT_FROM_EMAIL,
#             ["aurotechltd@gmail.com"],  # where you receive the quote
#             fail_silently=False,
#         )

#         # -------------------------------
#         # Success message
#         # -------------------------------
#         messages.success(request, "Your quote request has been submitted successfully.")

#         return render(
#             request,
#             "aurotech/quote_success.html",
#             {"product": product}
#         )

#     return render(request, "aurotech/request_quote.html", {"product": product})