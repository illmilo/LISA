from django.shortcuts import render

# Create your views here.
def activities(request):
    return render(request, "activities/activities.html")

def activity_detail(request, activity_id):
    return render(request, "activities/activity_detail.html", {"activity_id": activity_id})

def create_activity(request):
    return render(request, "activities/activity_create.html")

def edit_activity(request, activity_id):
    return render(request, "activities/activity_form.html", {"mode": "edit", "activity_id": activity_id})

def delete_activity(request, activity_id):
    return render(request, "activities/activity_delete.html", {"activity_id": activity_id})
