from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterUserForm

def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_url')
    else:
        form = RegisterUserForm()
    return render(request, 'authenticate/register.html', {'form': form})
