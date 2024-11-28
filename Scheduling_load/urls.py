from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ctu_scheduler/', include('scheduling_system.urls')),  # Base path for your app
    path('', lambda request: redirect('ctu_scheduler/', permanent=False)),  # Redirect root to ctu_scheduler

]
