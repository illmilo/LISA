from django.shortcuts import redirect, render

def agents(request):
    print("hello")
    return render(request, "agents/agents.html")
