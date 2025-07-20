from django.shortcuts import render

def servers(request):
    return render(request, "servers/servers.html")

def server_detail(request, server_id):
    return render(request, "servers/server_detail.html", {"server_id": server_id})

def edit_server(request, server_id):
    return render(request, "servers/server_form.html", {"server_id": server_id})

def create_server(request):
    return render(request, "servers/server_create.html")
