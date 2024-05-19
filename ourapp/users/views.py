from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .serializer import UserSerializer
from django.http import FileResponse
import os

# Декоратор для выдачи ошибки если пользователь неавторизован
def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@login_required
def profile(request):
    return render(request, 'users/profile.html')

# Создаёт уникальный CSRF-токен и вставляет в cookie браузеру
def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response

# Узнать авторизован ли пользователь и получить его данные
@ensure_csrf_cookie # <- Принудительная отправка CSRF cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True, 'username': request.user.username, 'user_id': request.user.id})

# Получение информации о пользователе
@json_login_required
def user_info(request):
    user = request.user
    serializer = UserSerializer(user)
    data = serializer.data
    data['image'] = user.profile.image.url if user.profile.image else None
    print("USER ", data)
    return JsonResponse(data)

@require_POST
def login_view(request):
    # Получаем авторизационные данные
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    # Валидация
    if username is None or password is None:
        return JsonResponse({'detail': 'Пожалуйста предоставьте логин и пароль'}, status=400)

    # Аутентификация пользоваля
    user = authenticate(username=username, password=password)
    
    if user is None:
        return JsonResponse({'detail': 'Неверные данные'}, status=400)

    # Создаётся сессия. session_id отправляется в куки
    login(request, user)
    return JsonResponse({'detail': 'Успешная авторизация'})

@csrf_exempt
@require_POST
def register_view(request):
    # Получаем данные для регистрации из запроса
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    # Валидация данных
    if username is None or password is None:
        return JsonResponse({'detail': 'Пожалуйста, предоставьте логин, пароль, имя и фамилию'}, status=400)

    # Проверяем, существует ли пользователь с таким именем
    if User.objects.filter(username=username).exists():
        return JsonResponse({'detail': 'Пользователь с таким логином уже существует'}, status=400)

    # Создаем нового пользователя
    user = User.objects.create_user(username=username, password=password, first_name=firstName, last_name=lastName)

    return JsonResponse({'detail': 'Успешная регистрация'})

@csrf_exempt
@require_POST
def update_user_view(request, user_id):
    # Получаем данные для обновления из запроса
    data = json.loads(request.body)
    username = data.get('username')
    firstName = data.get('first_name')
    lastName = data.get('last_name')
    email = data.get('email')

    # Проверяем, существует ли пользователь с указанным id
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'detail': 'Пользователь с указанным id не найден'}, status=404)

    # Обновляем данные пользователя
    if username:
        user.username = username
    if firstName:
        user.first_name = firstName
    if lastName:
        user.last_name = lastName
    if email:
        user.email = email

    user.save()

    return JsonResponse({'detail': 'Пользователь успешно обновлен'})

# Сессия удаляется из БД и session_id на клиенте более недействителен
@json_login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'detail': 'Вы успешно вышли'})

@json_login_required
@require_POST
def upload_photo(request):
    user = request.user
    image = request.FILES.get('image')
    print("IMAGE ", image)
    if image:
        # Сохранение фотографии пользователя
        user.profile.image = image
        user.profile.save()

        return JsonResponse({'detail': 'Фото успешно загружено'})
    else:
        return JsonResponse({'detail': 'Ошибка загрузки фото'}, status=400)
    
@json_login_required
def user_photo(request):
    user = request.user
    photo_path = user.profile.image.path if user.profile.image else None
    if photo_path and os.path.exists(photo_path):
        img = open(photo_path, 'rb')
        response = FileResponse(img, as_attachment=True)
        return response
    else:
        return JsonResponse({'detail': 'Фото не найдено'}, status=404)