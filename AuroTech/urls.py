from django.urls import path # pyright: ignore[reportMissingModuleSource]
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('core/<slug:slug>/', views.core_product_detail, name='core_product_detail'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.all_products, name='all_products'),
    path('search/', views.search_products, name='search_products'),
    path('about/', views.about_us, name='about_us'),
    
    
    
]
