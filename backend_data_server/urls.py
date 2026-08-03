from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('homepage/', include('homepage.urls')),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='security/login.html'),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
