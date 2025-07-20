from django.shortcuts import render

# Create your views here.
def roles(request):
    return render(request, "roles/roles.html")

def role_detail(request, role_id):
    return render(request, "roles/role_detail.html", {"role_id": role_id})

def edit_role(request, role_id):
    return render(request, "roles/role_form.html", {"role_id": role_id})

def create_role(request):
    return render(request, "roles/role_create.html")
