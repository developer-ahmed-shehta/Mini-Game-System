import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return JsonResponse({"message": "Login successful"})

        # If user does not exist, create and log in
        try:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return JsonResponse({"message": "User created and logged in"})
        except Exception as e:
            return JsonResponse({"error": f"Could not create user: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "logged out"})
