from django.contrib import admin
from django.urls import path, include
from predictor import views
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView

# Add a redirect view for the root URL
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Add explicit logout view
    path('', redirect_to_login),
]
