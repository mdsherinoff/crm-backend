"""
Run this once to seed the PostgreSQL database with sample CRM data.
Usage: python seed.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import Lead, Opportunity, Activity
from datetime import date, timedelta

def seed():
    # Create all tables first
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Skip if data already exists
        if db.query(Lead).count() > 0:
            print("Database already has data — skipping seed.")
            return

        today = date.today()

        # ── Leads ────────────────────────────────────────────────────────────
        leads = [
            Lead(lead_name="Sarah Mitchell",  company_name="Nexaflow Inc",       email="s.mitchell@nexaflow.com",   phone="+1-415-555-0101", source="Website",        status="Qualified", created_date=today - timedelta(days=45)),
            Lead(lead_name="James Okafor",    company_name="Bridgetek Solutions", email="j.okafor@bridgetek.io",    phone="+1-312-555-0188", source="Referral",       status="Qualified", created_date=today - timedelta(days=38)),
            Lead(lead_name="Priya Nair",      company_name="Luminary Labs",       email="p.nair@luminarylabs.com",  phone="+1-650-555-0234", source="Social Media",   status="Contacted", created_date=today - timedelta(days=30)),
            Lead(lead_name="Carlos Mendez",   company_name="Apex Retail Group",   email="c.mendez@apexretail.com",  phone="+1-214-555-0177", source="Cold Call",      status="New",       created_date=today - timedelta(days=25)),
            Lead(lead_name="Rachel Kim",      company_name="UrbanNest PropTech",  email="r.kim@urbannest.co",       phone="+1-212-555-0399", source="Email Campaign", status="Qualified", created_date=today - timedelta(days=20)),
            Lead(lead_name="Tom Hargreaves",  company_name="Ironclad Logistics",  email="t.hargreaves@ironclad.com",phone="+1-713-555-0421", source="Event",          status="Contacted", created_date=today - timedelta(days=18)),
            Lead(lead_name="Aisha Hassan",    company_name="GreenPath Energy",    email="a.hassan@greenpath.ae",    phone="+971-4-555-0155", source="Referral",       status="Qualified", created_date=today - timedelta(days=14)),
            Lead(lead_name="David Cheng",     company_name="Skybridge Capital",   email="d.cheng@skybridge.hk",     phone="+852-555-0290",   source="Website",        status="New",       created_date=today - timedelta(days=10)),
            Lead(lead_name="Elena Popescu",   company_name="Softwave Systems",    email="e.popescu@softwave.ro",    phone="+40-21-555-0311", source="Cold Call",      status="Lost",      created_date=today - timedelta(days=8)),
            Lead(lead_name="Marcus Webb",     company_name="Coastal Media Group", email="m.webb@coastalmedia.com",  phone="+1-305-555-0512", source="Social Media",   status="New",       created_date=today - timedelta(days=3)),
        ]
        db.add_all(leads)
        db.flush()  # flush to get lead_id values assigned

        # ── Opportunities ─────────────────────────────────────────────────────
        opportunities = [
            Opportunity(lead_id=leads[0].lead_id, opp_name="Nexaflow — Enterprise License",   deal_value=48000, stage="Negotiation",   probability=75,  expected_close_date=today + timedelta(days=15),  created_date=today - timedelta(days=44)),
            Opportunity(lead_id=leads[1].lead_id, opp_name="Bridgetek — Implementation Pack", deal_value=32000, stage="Proposal Sent", probability=50,  expected_close_date=today + timedelta(days=30),  created_date=today - timedelta(days=37)),
            Opportunity(lead_id=leads[4].lead_id, opp_name="UrbanNest — Starter Platform",    deal_value=15500, stage="Won",           probability=100, expected_close_date=today - timedelta(days=5),   created_date=today - timedelta(days=19)),
            Opportunity(lead_id=leads[6].lead_id, opp_name="GreenPath — Annual SaaS Plan",    deal_value=60000, stage="Proposal Sent", probability=55,  expected_close_date=today + timedelta(days=45),  created_date=today - timedelta(days=13)),
            Opportunity(lead_id=leads[0].lead_id, opp_name="Nexaflow — Support Add-on",       deal_value=9500,  stage="Won",           probability=100, expected_close_date=today - timedelta(days=12),  created_date=today - timedelta(days=40)),
            Opportunity(lead_id=leads[1].lead_id, opp_name="Bridgetek — Training Bundle",     deal_value=8200,  stage="Prospecting",   probability=20,  expected_close_date=today + timedelta(days=60),  created_date=today - timedelta(days=35)),
            Opportunity(lead_id=leads[6].lead_id, opp_name="GreenPath — Mobile App Module",   deal_value=22000, stage="Negotiation",   probability=80,  expected_close_date=today + timedelta(days=20),  created_date=today - timedelta(days=12)),
            Opportunity(lead_id=leads[4].lead_id, opp_name="UrbanNest — API Integration",     deal_value=75800, stage="Lost",          probability=0,   expected_close_date=today - timedelta(days=20),  created_date=today - timedelta(days=18)),
        ]
        db.add_all(opportunities)

        # ── Activities ────────────────────────────────────────────────────────
        activities = [
            Activity(lead_id=leads[0].lead_id, activity_type="Call",      notes="Introductory call — confirmed budget and timeline.",          activity_date=today - timedelta(days=43)),
            Activity(lead_id=leads[0].lead_id, activity_type="Email",     notes="Sent product brochure and pricing sheet.",                    activity_date=today - timedelta(days=40)),
            Activity(lead_id=leads[0].lead_id, activity_type="Meeting",   notes="Demo session with IT team. Moving to negotiation.",           activity_date=today - timedelta(days=20)),
            Activity(lead_id=leads[1].lead_id, activity_type="Call",      notes="Referral intro call. Needs proposal by end of month.",        activity_date=today - timedelta(days=36)),
            Activity(lead_id=leads[1].lead_id, activity_type="Email",     notes="Proposal sent covering enterprise and training options.",      activity_date=today - timedelta(days=28)),
            Activity(lead_id=leads[1].lead_id, activity_type="Follow-up", notes="No response to proposal yet. Sending follow-up.",             activity_date=today - timedelta(days=14)),
            Activity(lead_id=leads[2].lead_id, activity_type="Email",     notes="Responded to LinkedIn enquiry. Scheduled discovery call.",    activity_date=today - timedelta(days=28)),
            Activity(lead_id=leads[2].lead_id, activity_type="Call",      notes="Discovery call done. Evaluating 3 vendors.",                  activity_date=today - timedelta(days=22)),
            Activity(lead_id=leads[4].lead_id, activity_type="Call",      notes="Email campaign response. Keen to start with starter plan.",   activity_date=today - timedelta(days=19)),
            Activity(lead_id=leads[4].lead_id, activity_type="Meeting",   notes="Contract signing. Starter plan closed.",                      activity_date=today - timedelta(days=5)),
            Activity(lead_id=leads[5].lead_id, activity_type="Call",      notes="Met at logistics trade show. Following up next week.",        activity_date=today - timedelta(days=16)),
            Activity(lead_id=leads[5].lead_id, activity_type="Follow-up", notes="Left voicemail and sent email. Awaiting response.",           activity_date=today - timedelta(days=9)),
            Activity(lead_id=leads[6].lead_id, activity_type="Meeting",   notes="In-person meeting. Strong interest in annual plan.",          activity_date=today - timedelta(days=12)),
            Activity(lead_id=leads[6].lead_id, activity_type="Email",     notes="Sent revised proposal with bundle discount.",                 activity_date=today - timedelta(days=7)),
            Activity(lead_id=leads[8].lead_id, activity_type="Call",      notes="Cold call — went with a competitor. Marked Lost.",            activity_date=today - timedelta(days=6)),
        ]
        db.add_all(activities)
        db.commit()

        print(f"✓ Seeded {len(leads)} leads")
        print(f"✓ Seeded {len(opportunities)} opportunities")
        print(f"✓ Seeded {len(activities)} activities")
        print("Database ready.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()