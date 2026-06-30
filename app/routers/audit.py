from fastapi import APIRouter, HTTPException, Query
from kafka import KafkaConsumer
import json
import os
import time
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

TOPICS = ["crm.leads", "crm.deals"]


class EventRecord(BaseModel):
    topic:     str
    partition: int
    offset:    int
    key:       Optional[str]
    event:     str
    payload:   dict


class AuditSummary(BaseModel):
    total_events: int
    topics:       dict
    event_types:  dict


def read_topic_from_start(topics: list, lead_id: int = None) -> List[EventRecord]:
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id=f"crm-audit-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=8000,
        session_timeout_ms=30000,
        heartbeat_interval_ms=3000,
    )

    # Wait until partitions are actually assigned before seeking
    assigned  = set()
    attempts  = 0
    while not assigned and attempts < 10:
        consumer.poll(timeout_ms=1000)
        assigned = consumer.assignment()
        attempts += 1
        if not assigned:
            time.sleep(1)

    if not assigned:
        consumer.close()
        raise RuntimeError("Could not get Kafka partition assignment after 10 attempts")

    consumer.seek_to_beginning(*assigned)

    records = []

    try:
        for message in consumer:
            raw_value = message.value
            raw_key   = message.key

            data = json.loads(raw_value.decode("utf-8")) if isinstance(raw_value, bytes) else raw_value
            key  = raw_key.decode("utf-8") if isinstance(raw_key, bytes) else (str(raw_key) if raw_key is not None else None)

            if lead_id:
                msg_lead_id = str(data.get("lead_id", ""))
                if key != str(lead_id) and msg_lead_id != str(lead_id):
                    continue

            records.append(EventRecord(
                topic=     message.topic,
                partition= message.partition,
                offset=    message.offset,
                key=       key,
                event=     data.get("event", "unknown"),
                payload=   data
            ))
    finally:
        consumer.close()

    return records


@router.get("/events", response_model=List[EventRecord])
def get_all_events(
    topic:   Optional[str] = Query(None, description="Filter by topic e.g. crm.leads"),
    lead_id: Optional[int] = Query(None, description="Filter by lead ID")
):
    """Return all events from Kafka — replays from offset 0 every time."""
    topics  = [topic] if topic else TOPICS
    try:
        records = read_topic_from_start(topics, lead_id=lead_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return records


@router.get("/events/lead/{lead_id}", response_model=List[EventRecord])
def get_lead_timeline(lead_id: int):
    """Return the complete event timeline for a specific lead."""
    try:
        records = read_topic_from_start(TOPICS, lead_id=lead_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No events found for lead {lead_id}"
        )
    return records


@router.get("/summary", response_model=AuditSummary)
def get_audit_summary():
    """Return a summary of all events in the Kafka stream."""
    try:
        records = read_topic_from_start(TOPICS)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    topic_counts = {}
    event_counts = {}

    for r in records:
        topic_counts[r.topic] = topic_counts.get(r.topic, 0) + 1
        event_counts[r.event] = event_counts.get(r.event, 0) + 1

    return AuditSummary(
        total_events=len(records),
        topics=topic_counts,
        event_types=event_counts
    )