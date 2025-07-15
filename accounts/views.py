from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'status': 'logged in'})
        return JsonResponse({'error': 'invalid credentials'}, status=400)