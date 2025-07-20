from django.shortcuts import render

# Create your views here.
def roles(request):
    return render(request, 'roles/roles.html')
