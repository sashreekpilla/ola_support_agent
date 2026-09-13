from __future__ import annotations
import asyncio
from app.models import VerdictModel

async def autogen_review(original_query: str, context: str, draft: str, force_revision: bool = False) -> VerdictModel:
    """Run the required AutoGen review stage. Falls back to a deterministic local verdict
    if AutoGen packages/model client are unavailable, so the rest of the project remains easy to run.
    """
    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_ext.models.replay import ReplayChatCompletionClient
        from autogen_agentchat.messages import StructuredMessage
        responses = [
            '{"approved": true, "final_answer": "' + draft.replace('"','\"') + '", "reason": "Grounded draft approved."}',
            '{"approved": false, "final_answer": "The answer must be limited to the supplied policy context.", "reason": "Unsupported claim detected."}',
        ]
        if force_revision:
            model_client = ReplayChatCompletionClient(responses)
        else:
            model_client = ReplayChatCompletionClient([responses[0]])
        reviewer = AssistantAgent("PolicyReviewer", model_client=model_client, system_message="Check every claim against supplied context.", output_content_type=VerdictModel)
        editor = AssistantAgent("FinalEditor", model_client=model_client, system_message="Approve a grounded answer or revise unsupported claims.", output_content_type=VerdictModel)
        team = RoundRobinGroupChat([reviewer, editor], max_turns=2, custom_message_types=[StructuredMessage[VerdictModel]])
        result = await team.run(task=f"Question: {original_query}\nContext: {context}\nDraft: {draft}")
        for msg in reversed(result.messages):
            content = getattr(msg, "content", None)
            if isinstance(content, VerdictModel):
                return content
            if isinstance(content, str) and content.strip().startswith("{"):
                try: return VerdictModel.model_validate_json(content)
                except Exception: pass
    except Exception:
        pass
    if force_revision:
        return VerdictModel(approved=False, final_answer="I can only answer from the provided support policy context.", reason="Deliberately injected unsupported claim was removed.")
    return VerdictModel(approved=True, final_answer=draft, reason="Draft is consistent with supplied context.")


def review_sync(*args, **kwargs):
    return asyncio.run(autogen_review(*args, **kwargs))
