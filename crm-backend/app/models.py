from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# What comes IN when creating a lead
class LeadCreate(BaseModel):
    lead_name:    str
    company_name: Optional[str] = None
    email:        Optional[str] = None
    phone:        Optional[str] = None
    source:       Optional[str] = None
    status:       str = "New"

# What goes OUT when returning a lead
class LeadResponse(BaseModel):
    lead_id:      int
    lead_name:    str
    company_name: Optional[str]
    email:        Optional[str]
    phone:        Optional[str]
    source:       Optional[str]
    status:       str
    created_date: Optional[date]

    class Config:
        from_attributes = True

# Generic API response wrapper
class APIResponse(BaseModel):
    success: bool
    message: str
    data:    Optional[dict] = None