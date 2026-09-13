from langchain_core.tools import tool
from app.db import get_ticket
from app.config import ESCALATION_THRESHOLD
from app.memory import retrieve_top

@tool
def search_policy(query: str) -> str:
    """Retrieve the most relevant Ola support policy excerpts for a question."""
    hits = retrieve_top(query, "fixed", 3)
    if not hits:
        return "NO_POLICY_CONTEXT"
    return "\n".join(f"[{d.metadata.get('document_id')}] {d.page_content}" for d, _ in hits)

@tool
def check_support_ticket_status(record_id: str) -> dict:
    """Look up one support ticket and calculate its escalation score."""
    row = get_ticket(record_id)
    if not row:
        return {"record_id": record_id, "error": "ticket_not_found"}
    recency = 1 - (row["days_since_created"] / 30)
    score = round(0.60 * int(row["escalated"]) + 0.40 * recency, 4)
    return {"record_id": record_id, "status": row["status"], "resolution_time_hours": row["resolution_time_hours"], "escalation_score": score, "recommend_escalation": score >= ESCALATION_THRESHOLD}
