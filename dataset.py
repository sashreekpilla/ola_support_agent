from __future__ import annotations
from random import Random
import json
from pathlib import Path

SEED = 260113
CATEGORIES = ["Billing", "Technical Issue", "Account Access", "Product Defect", "General Inquiry"]
STATUSES = ["Open", "In Progress", "Escalated", "Resolved", "Closed"]
CATEGORY_WEIGHTS = [0.22, 0.22, 0.18, 0.18, 0.20]
STATUS_WEIGHTS = [0.24, 0.28, 0.12, 0.22, 0.14]
RESOLUTION_HOURS = (2, 72)


def generate_tickets(n: int = 60) -> list[dict]:
    rng = Random(SEED)
    rows = []
    for i in range(1, n + 1):
        category = rng.choices(CATEGORIES, CATEGORY_WEIGHTS)[0]
        status = rng.choices(STATUSES, STATUS_WEIGHTS)[0]
        days = rng.randint(0, 30)
        rows.append({
            "record_id": f"TKT-{i:04d}",
            "category": category,
            "status": status,
            "resolution_time_hours": rng.randint(*RESOLUTION_HOURS),
            "days_since_created": days,
            "escalated": status == "Escalated" or (i % 15 == 0),
        })
    return rows


def validate(rows: list[dict]) -> None:
    assert len(rows) >= 40
    assert all(sum(r["category"] == c for r in rows) >= 3 for c in CATEGORIES)
    assert all(any(r["status"] == s for r in rows) for s in STATUSES)
    escalated = sum(r["escalated"] for r in rows) / len(rows)
    assert 0.10 <= escalated <= 0.30
    assert all(0 <= r["days_since_created"] <= 30 for r in rows)


def save(rows: list[dict]) -> None:
    Path("data").mkdir(exist_ok=True)
    Path("data/support_tickets.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


SUPPORT_TICKETS = generate_tickets()
validate(SUPPORT_TICKETS)

if __name__ == "__main__":
    save(SUPPORT_TICKETS)
    print(f"Generated {len(SUPPORT_TICKETS)} tickets with seed {SEED}.")
    for c in CATEGORIES:
        print(c, sum(r["category"] == c for r in SUPPORT_TICKETS))
    for s in STATUSES:
        print(s, sum(r["status"] == s for r in SUPPORT_TICKETS))
    print("Escalated %:", round(100 * sum(r["escalated"] for r in SUPPORT_TICKETS) / len(SUPPORT_TICKETS), 2))
