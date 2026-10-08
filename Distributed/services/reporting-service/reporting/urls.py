from django.urls import path
from projections import views

handler404 = views.not_found

urlpatterns = [
    path("api/v1/reports/orders/summary", views.orders_summary),
    path("api/v1/reports/orders", views.orders),
    path("api/v1/reports/inventory", views.inventory),
    path("api/v1/reports/revenue", views.revenue),
]
