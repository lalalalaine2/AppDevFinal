from django.contrib import admin
from django.urls import path, include
from predictor import views
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def redirect_if_not_authenticated(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('predict')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('predict/', login_required(views.predict), name='predict'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='home'), name='home'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
]
