from django.shortcuts import render, redirect
from django.http import HttpResponse

def home_page(request):
    if request.method == 'POST':
        return redirect('/')
    return render(request, 'home.html')
