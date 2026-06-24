from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.models import LeadCreate, LeadResponse, APIResponse
from typing import List

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("/", response_model=List[LeadResponse])
def get_all_leads():
    """Return all leads from the CRM database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lead_id, lead_name, company_name,
                       email, phone, source, status, created_date
                FROM   leads
                ORDER  BY created_date DESC
            """)
            cols = [col[0].lower() for col in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    return rows


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int):
    """Return a single lead by ID."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lead_id, lead_name, company_name,
                       email, phone, source, status, created_date
                FROM   leads
                WHERE  lead_id = :lead_id
            """, {"lead_id": lead_id})
            cols = [col[0].lower() for col in cur.description]
            row  = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")
    return dict(zip(cols, row))


@router.post("/", response_model=APIResponse)
def create_lead(lead: LeadCreate):
    """Create a new lead."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO leads
                    (lead_name, company_name, email,
                     phone, source, status, created_date)
                VALUES
                    (:lead_name, :company_name, :email,
                     :phone, :source, :status, SYSDATE)
            """, lead.model_dump())
        conn.commit()
    return APIResponse(success=True, message="Lead created successfully")