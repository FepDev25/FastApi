from typing import Optional
from pydantic import BaseModel, Field

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: Optional[int] = Field(default=1, ge=1, le=5)

class TicketCreate(TicketBase):
    """Schema para crear un ticket"""
    pass

class TicketUpdate(BaseModel):
    """Schema para actualizar un ticket"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    is_completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class TicketRead(TicketBase):
    """Schema para leer un ticket (respuesta de la API)"""
    id: int
    is_completed: bool
    
    class Config:
        from_attributes = True