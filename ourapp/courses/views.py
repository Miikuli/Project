from rest_framework import generics
from .models import Course
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Course, File, Comment
import base64

# Декоратор для выдачи ошибки если пользователь неавторизован
def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

@json_login_required
@require_POST
def createCourse(request):
    userId = request.POST.get('userId')
    title = request.POST.get('title')
    description = request.POST.get('description')
    files = request.FILES.getlist('files')

    try:
        user = User.objects.get(id=userId)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    course = Course.objects.create(title=title, description=description, user=user)

    for file in files:
        file_instance = File.objects.create(
            name=file.name,
            file=file
        )
        course.files.add(file_instance)
    course.save()

    return JsonResponse({'message': 'Курс создан успешно'}, status=status.HTTP_201_CREATED)

@csrf_exempt
@require_POST
def updateCourse(request, courseId):
    # Получаем данные для обновления из запроса
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description')

    # Проверяем, существует ли курс с указанным id
    try:
        course = Course.objects.get(id=courseId)
    except Course.DoesNotExist:
        return JsonResponse({'detail': 'Курс с указанным id не найден'}, status=404)

    # Обновляем данные курса
    if title:
        course.title = title
    if description:
        course.description = description

    course.save()

    return JsonResponse({'detail': 'Курса успешно обновлен'})

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
        'subscribedCoursesIds': subscribedCoursesIds,
        'files': [
            {
                'id': file.id,
                'name': file.name,
                'data': base64.b64encode(file.file.read()).decode('utf-8')
            } for file in course.files.all()
        ]
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

@json_login_required
@require_POST
def addFileToCourse(request, courseId):
    course = Course.objects.get(id=courseId)
    
    file_data = request.FILES.get('file')
    file_instance = File.objects.create(
        name=file_data.name,
        file=file_data
    )
    
    course.files.add(file_instance)
    course.save()
    
    return JsonResponse({'message': 'Файл добалвен успешно'}, status=status.HTTP_200_OK)

@json_login_required
@api_view(['DELETE'])
def deleteFileFromCourse(request, courseId, fileId):
    course = Course.objects.get(id=courseId)
    file_instance = File.objects.get(id=fileId)
    
    course.files.remove(file_instance)
    file_instance.delete()
    
    return JsonResponse({'message': 'Файл удален успешно'}, status=status.HTTP_200_OK)

@json_login_required
@require_POST
def createComment(request, courseId):
    data = json.loads(request.body)
    course = Course.objects.get(id=courseId)
    user = request.user
    
    comment_content = data.get('content')
    
    comment = Comment.objects.create(
        course=course,
        author=user,
        content=comment_content
    )
    
    comment_data = {
        'id': comment.id,
        'content': comment.content,
        'author': {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
        },
        'created_at': comment.created_at.isoformat()
    }
    
    return JsonResponse(comment_data, status=status.HTTP_201_CREATED)

@json_login_required
def getСourseСomments(request, courseId):
    comments = Comment.objects.filter(course_id=courseId).order_by('-created_at')
    
    comments_data = []
    for comment in comments:
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'username': comment.author.username,
                'firstName': comment.author.first_name,
                'lastName': comment.author.last_name,
            },
            'created_at': comment.created_at.isoformat()
        }
        comments_data.append(comment_data)
    
    return JsonResponse(comments_data, safe=False)