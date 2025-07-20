from django.urls import path
from . import views

urlpatterns = [
    path('', views.activities, name='activities'),
    path('<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('create/', views.create_activity, name='create_activity'),
    path('<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
]