from django.urls import path, include
from . import views
from .views import post_invoice_view, delete_time_entry
from django.contrib.auth import views as auth_views
from .forms import StyledAuthenticationForm
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Protected views requiring login
    path("index.html", login_required(views.index), name="index"),
    path("create_invoice.html", login_required(views.create_invoice),
         name="create-invoice"),
    path("record.html", login_required(views.record_time),
         name="record-time"),
    path("view_invoice.html", login_required(views.view_invoice),
         name="view-invoice"),
    path("invoices/post/", login_required(post_invoice_view),
         name="post-invoice"),
    # Customized login view with styled form
    path("accounts/login/", auth_views.LoginView.as_view(
        authentication_form=StyledAuthenticationForm,
        template_name="registration/login.html",
    ), name="login"),
    # Overrides default password reset to use custom template
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),
    # login, logout, password change/reset
    path("accounts/", include("django.contrib.auth.urls")),
    # Ajax endpoint for dynamic matter options
    path("ajax/matter-options/", views.ajax_matter_options,
         name="ajax-matter-options"),
    # Delete time entry
    path("time-entry/<int:pk>/delete/", delete_time_entry,
         name="timeentry-delete"),

]

handler404 = "better_bill_project.views.custom_404"
