from pydantic import BaseModel, Field, ConfigDict
from typing import List

class RoleNameSchema(BaseModel):
    id: int
    name: str

class RoleCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    activity_ids: List[int] = Field(default_factory=list)

class RoleUpdateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    activity_ids: List[int] = Field(default_factory=list)

class RoleSchema(BaseModel):
    id: int
    name: str
    activity_ids: List[int]
    model_config = ConfigDict(from_attributes=True)
