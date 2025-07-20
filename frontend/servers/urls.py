from django.urls import path
from . import views

urlpatterns = [
    path('', views.servers, name='servers'),
    path('<int:server_id>/', views.server_detail, name='server_detail'),
    path('<int:server_id>/edit/', views.edit_server, name='edit_server'),
    path('create/', views.create_server, name='create_server'),
]