from django.urls import path
from . import views

urlpatterns = [
    path('', views.roles, name='roles'),
    path('<int:role_id>/', views.role_detail, name='role_detail'),
    path('<int:role_id>/edit/', views.edit_role, name='edit_role'),
    path('create/', views.create_role, name='create_role'),
]