from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import quote
import requests

from .models import CoreProduct, Product, QuoteRequest

# -------------------------------
# CONTACT FORM
# -------------------------------
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
        return redirect('contact')

    return render(request, 'aurotech/contact.html')


# -------------------------------
# HOMEPAGE
# -------------------------------
def home(request):
    core_products = CoreProduct.objects.all()
    return render(request, 'aurotech/index.html', {
        'core_products': core_products
    })


# -------------------------------
# CORE PRODUCT PAGE
# -------------------------------
def core_product_detail(request, slug):
    core_product = get_object_or_404(CoreProduct, slug=slug)
    products = core_product.products.all()

    return render(request, 'aurotech/core_product_detail.html', {
        'core_product': core_product,
        'products': products
    })


# -------------------------------
# PRODUCT DETAIL
# -------------------------------
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'aurotech/product_detail.html', {'product': product})


# -------------------------------
# ALL PRODUCTS
# -------------------------------
def all_products(request):
    products = Product.objects.all()
    return render(request, 'aurotech/all_products.html', {'products': products})


# -------------------------------
# SERVICES PAGE
# -------------------------------
def services(request):
    return render(request, "aurotech/services.html")


# -------------------------------
# SEARCH PRODUCTS
# -------------------------------
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


# -------------------------------
# ABOUT US
# -------------------------------
def about_us(request):
    return render(request, 'aurotech/about_us.html')


# -------------------------------
# ODOO CONFIGURATION
# -------------------------------
ODOO_URL = "https://aurotech-solutions-limited1.odoo.com/"
API_KEY = "YOUR_API_KEY"
DB = "aurotech-solutions-limited1"
USER_ID = 2


def create_or_get_partner(name, email, company, phone):
    """Create or fetch a partner in Odoo."""
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
        response = requests.post(f"{ODOO_URL}/jsonrpc", json=payload).json()
        if response.get("result"):
            return response["result"][0]["id"]
    except Exception as e:
        print("Partner check error:", e)

    # Create if not found
    payload_create = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB, USER_ID, API_KEY,
                "res.partner", "create",
                [{
                    "name": name,
                    "email": email,
                    "company_type": "company" if company else "person",
                    "phone": phone
                }]
            ]
        },
        "id": 2
    }
    try:
        response_create = requests.post(f"{ODOO_URL}/jsonrpc", json=payload_create).json()
        return response_create.get("result")
    except Exception as e:
        print("Partner creation error:", e)
        return None


def create_sale_order_multi(partner_id, order_lines, message):
    """Create sale order in Odoo."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                DB, USER_ID, API_KEY,
                "sale.order", "create",
                [{
                    "partner_id": partner_id,
                    "note": message,
                    "order_line": order_lines
                }]
            ]
        },
        "id": 3
    }
    try:
        response = requests.post(f"{ODOO_URL}/jsonrpc", json=payload).json()
        return response.get("result")
    except Exception as e:
        print("Sale order error:", e)
        return None


# -------------------------------
# MULTI PRODUCT QUOTE REQUEST
# -------------------------------
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
                email_lines += f"{product.name} - Quantity: {qty}\n"

                if product.odoo_id:
                    order_lines.append(
                        (0, 0, {
                            "product_id": product.odoo_id,
                            "product_uom_qty": qty
                        })
                    )

                QuoteRequest.objects.create(
                    product=product,
                    name=name,
                    company=company,
                    email=email,
                    phone=phone,
                    quantity=qty,
                    message=message
                )

        if not selected_any:
            messages.error(request, "Please select at least one product.")
            return render(request, "aurotech/request_multi_quote.html", {"products": products})

        # -------------------------------
        # SEND EMAIL VIA SMTP
        # -------------------------------
        subject = "Quote Request - Aurotech"
        email_body = f"""
New Quote Request

Name: {name}
Company: {company}
Email: {email}
Phone: {phone}

Products Requested:
{email_lines}

Message:
{message}
"""
        try:
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            print("Email sending error:", e)
            messages.error(request, "Failed to send email. Please try again later.")
            return render(request, "aurotech/request_multi_quote.html", {"products": products})

        # -------------------------------
        # CREATE ODOO SALE ORDER
        # -------------------------------
        try:
            partner_id = create_or_get_partner(name, email, company, phone)
            if partner_id:
                create_sale_order_multi(partner_id, order_lines, message)
        except Exception as e:
            print("Odoo integration error:", e)

        messages.success(request, "Your quote request has been submitted successfully!")
        return redirect("request_multi_quote")

    return render(request, "aurotech/request_multi_quote.html", {"products": products})