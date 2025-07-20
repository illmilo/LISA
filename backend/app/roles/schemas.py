from pydantic import BaseModel, Field
from typing import List, Optional
from app.activities.schemas import ActivitySchema, ActivityShallowSchema

class RoleBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Название роли")

class RoleCreateSchema(RoleBaseSchema):
    pass

class RoleUpdateSchema(RoleBaseSchema):
    pass

class RoleSchema(RoleBaseSchema):
    name: str
    id: int
    activities: Optional[List[ActivityShallowSchema]] = Field(default_factory=list)
    class Config:
        from_attributes = True

class RoleSetActivitiesSchema(BaseModel):
    activity_ids: List[int] = Field(..., description="Список id активностей для роли")

class RoleNameSchema(BaseModel):
    name: str
