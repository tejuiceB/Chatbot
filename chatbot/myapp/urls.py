from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('chat/', views.chat, name='chat'),
    path('hospitals/', views.hospitals, name='hospitals'),
    path('blogs/', views.blogs, name='blogs'),
    path('add_blog/', views.add_blog, name='add_blog'),
    path('doctors/', views.doctors, name='doctors'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='/password_change/done/'
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ),
         name='password_change_done'),
]
