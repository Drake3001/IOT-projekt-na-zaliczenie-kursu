"""
URL configuration for system_rfid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
import core.views as views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('logout/', views.logout_worker, name='logout'),

    path('', views.home, name='home'),
    
    path('cards/', views.card_list, name='card_list'),
    path('logs/', views.log_list, name='log_list'),
    
    path('api/latest/', views.api_latest_log, name='api_latest_log'),

    path('register/', views.start_register, name='start_register'),
    path('card/extend/<int:card_id>/', views.extend_validity, name='extend_validity'),
    path('card/block/<int:card_id>/', views.block_card, name='block'),
]
