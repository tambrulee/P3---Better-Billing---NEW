from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from .forms import TimeEntryForm
from .models import TimeEntry

# Create your views here.

def index(request):
    return render(request, "better_bill_project/index.html")

def create_invoice(request):
    return render(request, "better_bill_project/create_invoice.html")

def record_time(request):
    if request.method == "POST":
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f"Time entry saved for {entry.matter.matter_number}")
            return redirect("record-time")
    else:
        form = TimeEntryForm()

    recent_entries = TimeEntry.objects.select_related("matter", "fee_earner").order_by("-created_at")[:10]
    return render(request, "better_bill_project/record.html", {"form": form, "recent_entries": recent_entries})

def view_invoice(request):
    return render(request, "better_bill_project/view_invoice.html")


