from django.urls import path
from . import views

urlpatterns = [
    path("create_invoice.html", views.create_invoice, name="create-invoice"),

]
