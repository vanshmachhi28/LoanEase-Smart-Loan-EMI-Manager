from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = form.cleaned_data.get('role')

            # SAFE profile creation
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': role}
            )

            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
