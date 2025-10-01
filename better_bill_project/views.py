from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, "better_bill_project/templates/index.html")

def create_invoice(request):
    return render(request, "better_bill_project/templates/create_invoice.html")