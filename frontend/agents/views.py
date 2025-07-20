from django.shortcuts import render

def agents(request):
    return render(request, "agents/agents.html")

def agent_detail(request, agent_id):
    return render(request, "agents/agent_detail.html", {"agent_id": agent_id})

def edit_agent(request, agent_id):
    return render(request, "agents/agent_form.html", {"agent_id": agent_id})

def create_agent(request):
    return render(request, "agents/agent_create.html")
