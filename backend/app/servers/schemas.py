from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ServerCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    password: str
    server_key: str
    employee_ids: List[int] = Field(default_factory=list)

class ServerUpdateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    password: str
    server_key: str
    employee_ids: List[int] = Field(default_factory=list)

class ServerSchema(BaseModel):
    id: int
    name: str
    password: str
    server_key: str
    employee_ids: List[int]
    model_config = ConfigDict(from_attributes=True)
