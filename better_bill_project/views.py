from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, "better_bill_project/index.html")

def create_invoice(request):
    return render(request, "better_bill_project/create_invoice.html")

def record_time(request):
    return render(request, "better_bill_project/record.html")

def view_invoice(request):
    return render(request, "better_bill_project/view_invoice.html")