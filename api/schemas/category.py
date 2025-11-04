# app/schemas/category.py
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Union
from api.models.category import CategoryType


class CategoryBase(BaseModel):
    name: str
    # accept either the enum or a string (case-insensitive) from clients
    type: Union[CategoryType, str]

    @validator("type", pre=True)
    def validate_type(cls, v):
        # allow passing the enum instance through
        if isinstance(v, CategoryType):
            return v
        if isinstance(v, str):
            lowered = v.lower()
            for ct in CategoryType:
                if lowered == ct.value:
                    return ct
        raise ValueError("type must be one of: 'despesa' or 'receita'")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
