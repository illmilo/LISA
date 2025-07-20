from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls')),
    path('agents/', include('agents.urls')),
    path('servers/', include('servers.urls')),
    path('roles/', include('roles.urls')),
    path('activities/', include('activities.urls')),
]
