from django.urls import path
from . import views

urlpatterns = [
    path('', views.agents, name='agents'),
    path('<int:agent_id>/', views.agent_detail, name='agent_detail'),
    path('<int:agent_id>/edit/', views.edit_agent, name='edit_agent'),
    path('create/', views.create_agent, name='create_agent'),
]