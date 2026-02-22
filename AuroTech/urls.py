from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('core/<slug:slug>/', views.core_product_detail, name='core_product_detail'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    
    
]
