from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from courses import views as courses_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register_view, name='register'),
    path('', include('main.urls')),
    path('profile/', user_views.profile, name='profile'),
    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('csrf/', user_views.get_csrf, name='csrf'),
    path('logout/', user_views.logout_view, name='logout'),
    path('session/', user_views.session_view, name='session'),
    path('user_info/', user_views.user_info, name='user_info'),
    path('users/', user_views.users_list, name='users'),
    path('login/', user_views.login_view, name='login'),
    path('users/<int:user_id>/update/', user_views.update_user_view, name='update_user'),
    path('upload_photo/', user_views.upload_photo, name='upload_photo'),
    path('user/photo/', user_views.user_photo, name='user_photo'),

    path('courses/', courses_views.getCourses, name='courses'),
    path('courses/create/', courses_views.createCourse, name='create_course'),
    path('courses/<int:courseId>/', courses_views.getСourseById, name='course-detail'),
    path('courses/subscribe/', courses_views.subscribeСourse, name='subscribeСourse'),
    path('courses/unsubscribe/', courses_views.unsubscribeCourse, name='unsubscribeCourse'),
    path('courses/my/', courses_views.getSubscribedCourses, name='myCourses'),
    path('courses/myCreated/', courses_views.getMyCreatedCourses, name='myCreatedCourses'),
    path('courses/<int:courseId>/update/', courses_views.updateCourse, name='update_course'),
    path('courses/<int:courseId>/files/create/', courses_views.addFileToCourse, name='addFileToCourse'),
    path('courses/<int:courseId>/files/<int:fileId>/delete/', courses_views.deleteFileFromCourse, name='deleteFileFromCourse'),

    path('courses/<int:courseId>/comments/create/', courses_views.createComment, name='createComment'),
    path('courses/<int:courseId>/comments/', courses_views.getСourseСomments, name='getСourseСomments'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)