from django.urls import path, include
from . import views
from .views import index, post_invoice_view, record_time, delete_time_entry
from django.contrib.auth import views as auth_views
from .forms import StyledAuthenticationForm
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("index.html", login_required(views.index), name="index"),
    path("create_invoice.html", login_required(views.create_invoice), name="create-invoice"),
    path("record.html", login_required(views.record_time), name="record-time"),
    path("view_invoice.html", login_required(views.view_invoice), name="view-invoice"),
    path("invoices/post/", login_required(post_invoice_view), name="post-invoice"),
    path("accounts/login/", auth_views.LoginView.as_view(
        authentication_form=StyledAuthenticationForm,
        template_name="registration/login.html",
    ), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),  # login, logout, password change/reset
    path("ajax/matter-options/", views.ajax_matter_options, name="ajax-matter-options"),
   path("time-entry/<int:pk>/delete/", delete_time_entry, name="timeentry-delete"),

]

handler404 = "better_bill_project.views.custom_404"