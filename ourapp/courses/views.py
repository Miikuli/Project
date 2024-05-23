from rest_framework import generics
from .models import Course
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view

# Декоратор для выдачи ошибки если пользователь неавторизован
def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@json_login_required
@api_view(['POST'])
def createCourse(request):
    userId = request.data.get('userId')
    title = request.data.get('title')
    description = request.data.get('description')
    # files_data = request.data.get('files')

    try:
        user = User.objects.get(id=userId)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    course = Course.objects.create(title=title, description=description, user=user)

    # for file_data in files_data:
    #     file = File.objects.create(name=file_data.get('name'), file_url=file_data.get('file_url'))
    #     course.files.add(file)
    # course.users.add(user)
    course.save()
    

    return JsonResponse({'message': 'Курс создан успешно'}, status=status.HTTP_201_CREATED)

# Получение всех курсов
@json_login_required
def getCourses(request):
    coursesList = []
    courses = Course.objects.all()
    for course in courses:
        course_dict = {}
        user_dict = {}
        course_dict['id'] = course.id
        course_dict['title'] = course.title
        course_dict['description'] = course.description
        course_dict['createdAt'] = course.created_at
        
        user_dict['firstName'] = course.user.first_name
        user_dict['lastName'] = course.user.last_name
        
        course_dict['user'] = user_dict
        
        coursesList.append(course_dict)

    coursesList = list(coursesList)
    return JsonResponse(coursesList, safe=False)

@json_login_required
def getСourseById(request, courseId):
    user = request.user
    try:
        course = Course.objects.get(id=courseId)

        subscribedCoursesIds = []
        subscribed_courses = user.subscribed_courses.all()
        for subscribed_course in subscribed_courses:
            subscribedCoursesIds.append(subscribed_course.id)

        subscribedCoursesIds = list(subscribedCoursesIds)
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Курс не найден'}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'created_at': course.created_at,
        'user': {
            'id': course.user.id,
            'firstName': course.user.first_name,
            'lastName': course.user.last_name,
        },
        'subscribedCoursesIds': subscribedCoursesIds
    }

    return JsonResponse(data, status=status.HTTP_200_OK)

@json_login_required
def getSubscribedCourses(request):
    user = request.user

    subscribed_courses = user.subscribed_courses.all()

    coursesList = []
    for course in subscribed_courses:
        course_dict = {}
        user_dict = {}
        course_dict['id'] = course.id
        course_dict['title'] = course.title
        course_dict['description'] = course.description
        course_dict['createdAt'] = course.created_at
        
        user_dict['firstName'] = course.user.first_name
        user_dict['lastName'] = course.user.last_name
        
        course_dict['user'] = user_dict
        
        coursesList.append(course_dict)

    coursesList = list(coursesList)

    return JsonResponse(coursesList, status=status.HTTP_200_OK, safe=False)

@json_login_required
def getMyCreatedCourses(request):
    user = request.user

    created_courses = user.created_courses.all()

    coursesList = []
    for course in created_courses:
        course_dict = {}
        user_dict = {}
        course_dict['id'] = course.id
        course_dict['title'] = course.title
        course_dict['description'] = course.description
        course_dict['createdAt'] = course.created_at
        
        user_dict['firstName'] = course.user.first_name
        user_dict['lastName'] = course.user.last_name
        
        course_dict['user'] = user_dict
        
        coursesList.append(course_dict)

    coursesList = list(coursesList)

    return JsonResponse(coursesList, status=status.HTTP_200_OK, safe=False)

@json_login_required
@api_view(['POST'])
def subscribeСourse(request):
    user = request.user
    courseId = request.data.get('courseId')

    try:
        course = Course.objects.get(id=courseId)
    except (User.DoesNotExist, Course.DoesNotExist):
        return JsonResponse({'error': 'Пользователь или курс не найден'}, status=status.HTTP_404_NOT_FOUND)

    course.subscribers.add(user)
    course.save()

    return JsonResponse({'message': 'Подписка на курс успешна'}, status=status.HTTP_200_OK)

@json_login_required
@api_view(['POST'])
def unsubscribeCourse(request):
    user = request.user
    courseId = request.data.get('courseId')

    try:
        course = Course.objects.get(id=courseId)
    except (User.DoesNotExist, Course.DoesNotExist):
        return JsonResponse({'error': 'Пользователь или курс не найден'}, status=status.HTTP_404_NOT_FOUND)

    print(user.id, course.id)
    course.subscribers.remove(user)

    return JsonResponse({'message': 'Отписка от курса успешна'}, status=status.HTTP_200_OK)