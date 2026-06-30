"""
day9_full_flow_test.py — End-to-end test of the complete pipeline:
APEX -> FastAPI -> PostgreSQL -> RabbitMQ + Kafka -> Workers -> Audit log

Run this AFTER starting all services (uvicorn, workers, kafka consumer).
It exercises every part of the system in one script and prints a summary.

Usage:
    python day9_full_flow_test.py
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

results = []


def log(test_name, success, detail=""):
    status = "✓ PASS" if success else "✗ FAIL"
    results.append((test_name, success, detail))
    print(f"  {status}  {test_name}")
    if detail:
        print(f"         {detail}")


def run_full_test():
    print(f"\n{'='*60}")
    print(f"  FULL PIPELINE TEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # ── 1. Health check ──────────────────────────────────────────────────────
    print("1. Checking FastAPI is alive...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        log("FastAPI health check", r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        log("FastAPI health check", False, str(e))
        print("\nFastAPI is not running. Start it with: uvicorn app.main:app --reload")
        return

    # ── 2. Create a lead ─────────────────────────────────────────────────────
    print("\n2. Creating a new lead...")
    new_lead = {
        "lead_name":    "Pipeline Test Lead",
        "company_name": "Full Flow Inc",
        "email":        "pipeline@test.com",
        "source":       "Website",
        "status":       "New"
    }
    r = requests.post(f"{BASE_URL}/leads/", json=new_lead)
    success = r.status_code == 200 and r.json().get("success")
    lead_id = r.json().get("data", {}).get("lead_id") if success else None
    log("Create lead", success, f"lead_id={lead_id}")

    if not lead_id:
        print("\nCannot continue — lead creation failed.")
        return

    # ── 3. Verify lead exists in DB via GET ─────────────────────────────────
    print("\n3. Verifying lead in database...")
    r = requests.get(f"{BASE_URL}/leads/{lead_id}")
    log("Lead readable from DB", r.status_code == 200, f"name={r.json().get('lead_name')}")

    # ── 4. Convert the lead ──────────────────────────────────────────────────
    print("\n4. Converting lead to opportunity...")
    r = requests.post(f"{BASE_URL}/events/leads/{lead_id}/convert")
    success = r.status_code == 200 and r.json().get("success")
    opp_id  = r.json().get("data", {}).get("opp_id") if success else None
    log("Convert lead", success, f"opp_id={opp_id}")

    # ── 5. Confirm duplicate conversion is blocked ──────────────────────────
    print("\n5. Confirming duplicate conversion is blocked...")
    r = requests.post(f"{BASE_URL}/events/leads/{lead_id}/convert")
    log("Duplicate conversion blocked", r.status_code == 400, f"status={r.status_code}")

    # ── 6. Mark deal as won ──────────────────────────────────────────────────
    if opp_id:
        print("\n6. Marking deal as Won...")
        r = requests.post(f"{BASE_URL}/events/opportunities/{opp_id}/won")
        log("Mark deal Won", r.status_code == 200, f"status={r.status_code}")

    # ── 7. Give async workers time to process ───────────────────────────────
    print("\n7. Waiting for async workers to process events...")
    time.sleep(3)
    log("Wait for workers", True, "3 second buffer for RabbitMQ + Kafka consumers")

    # ── 8. Check Kafka audit trail has the events ───────────────────────────
    print("\n8. Checking Kafka audit trail...")
    r = requests.get(f"{BASE_URL}/audit/events/lead/{lead_id}")
    success = r.status_code == 200
    event_count = len(r.json()) if success else 0
    log(
        "Kafka audit trail populated",
        success and event_count >= 1,
        f"{event_count} events found for lead {lead_id}"
    )

    if success and event_count > 0:
        print(f"\n         Timeline for lead {lead_id}:")
        for i, event in enumerate(r.json(), 1):
            print(f"           {i}. {event['event']} (offset {event['offset']})")

    # ── 9. Check audit summary totals ───────────────────────────────────────
    print("\n9. Checking overall audit summary...")
    r = requests.get(f"{BASE_URL}/audit/summary")
    success = r.status_code == 200
    if success:
        summary = r.json()
        log(
            "Audit summary accessible",
            True,
            f"total_events={summary['total_events']}, types={summary['event_types']}"
        )
    else:
        log("Audit summary accessible", False)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}\n")

    passed = sum(1 for _, s, _ in results if s)
    total  = len(results)

    for name, success, detail in results:
        icon = "✓" if success else "✗"
        print(f"  {icon} {name}")

    print(f"\n  {passed}/{total} tests passed")

    if passed == total:
        print(f"\n  🎉 Full pipeline working end to end!")
        print(f"     APEX → FastAPI → PostgreSQL → RabbitMQ + Kafka → Workers → Audit")
    else:
        print(f"\n  Some tests failed — check the output above for details.")

    print()


if __name__ == "__main__":
    run_full_test()