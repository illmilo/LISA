from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.employees.router import router_employees
from app.activities.router import router_activities
from app.servers.router import router_servers
from app.roles.router import router_roles


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "LISA"}

app.include_router(router_employees)
app.include_router(router_activities)
app.include_router(router_servers)
app.include_router(router_roles)