from django.urls import path, include
from . import views
from .views import post_invoice_view
from django.contrib.auth import views as auth_views
from .forms import StyledAuthenticationForm
from .views import index

urlpatterns = [
    path("index.html", views.index, name="index"),
    path("create_invoice.html", views.create_invoice, name="create-invoice"),
    path("record.html", views.record_time, name="record-time"),
    path("view_invoice.html", views.view_invoice, name="view-invoice"),
    path("invoices/post/", post_invoice_view, name="post-invoice"),
    path("accounts/login/", auth_views.LoginView.as_view(
        authentication_form=StyledAuthenticationForm,
        template_name="registration/login.html",
    ), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),  # login, logout, password change/reset
    path("ajax/matter-options/", views.ajax_matter_options, name="ajax-matter-options"),
]

handler404 = "better_bill_project.views.custom_404"