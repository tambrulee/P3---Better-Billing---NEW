from django.urls import path
from . import views

urlpatterns = [
    path("index.html", views.index, name="index"),
    path("create_invoice.html", views.create_invoice, name="create-invoice"),
    path("record.html", views.record_time, name="record-time"),
    path("view_invoice.html", views.view_invoice, name="view-invoice"),

]
