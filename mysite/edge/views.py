from django.shortcuts import render, redirect
from django.http import HttpResponse

def home_page(request):
    if request.method == 'POST':
        return redirect('/proteins/the-only-protein-in-the-world')
    return render(request, 'home.html')

def protein_setup(request):
    return render(request, 'setup.html')
