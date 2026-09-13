from __future__ import annotations
import re, json, os
from crewai import Agent, Task, Crew, Process
try:
    from crewai import BaseLLM
except ImportError:
    BaseLLM = object
from app.tools import search_policy, check_support_ticket_status
from app.models import SupportResponse

class MockCrewLLM(BaseLLM):
    """Tiny deterministic BaseLLM used by CrewAI in MOCK_LLM mode.
    It intentionally returns a final answer for the required deterministic demos.
    Tool execution is demonstrated by the pipeline before the crew kickoff; the crew
    still receives and is configured with the tools as required by the brief.
    """
    def __init__(self):
        if BaseLLM is not object:
            super().__init__(model="mock-crew", temperature=0, api_key="not-required")

    def call(self, messages, tools=None, callbacks=None, available_functions=None, **kwargs):
        text = messages[-1].get("content", "") if isinstance(messages, list) else str(messages)
        if "Retrieved policy" in text or "Ticket lookup" in text or "compose" in text.lower():
            return "I can answer this using the retrieved policy and ticket information supplied by the earlier steps."
        return "I can answer only from the support policy and ticket information available to the system."


def llm():
    if os.getenv("MOCK_LLM", "true").lower() == "true":
        return MockCrewLLM()
    raise RuntimeError("Set MOCK_LLM=true or add a real CrewAI LLM implementation.")


def build_crew():
    model = llm()
    retrieval_agent = Agent(role="Retrieval Agent", goal="Find relevant Ola support-policy facts", backstory="You retrieve policy facts and do not invent them.", tools=[search_policy], llm=model, verbose=False, allow_delegation=False, max_iter=2)
    lookup_agent = Agent(role="Lookup Agent", goal="Check support-ticket status", backstory="You are the only agent allowed to access ticket records.", tools=[check_support_ticket_status], llm=model, verbose=False, allow_delegation=False, max_iter=2)
    composer = Agent(role="Response Composer", goal="Create a concise customer-support draft from supplied evidence", backstory="You combine retrieved facts without adding unsupported claims.", llm=model, verbose=False, allow_delegation=False, max_iter=1)
    return retrieval_agent, lookup_agent, composer


def run_crew(query: str, policy_context: str = "", ticket_context: dict | None = None):
    retrieval, lookup, composer = build_crew()
    t1=Task(description=f"Retrieve policy evidence for: {query}. Policy context: {policy_context}", expected_output="Relevant policy evidence.", agent=retrieval)
    t2=Task(description=f"Check ticket information if relevant to: {query}. Ticket context: {ticket_context or 'none'}", expected_output="Ticket status information or state that no ticket lookup is needed.", agent=lookup)
    t3=Task(description=f"Compose a final draft for the user. Query: {query}. Retrieved policy: {policy_context}. Ticket result: {ticket_context or 'none'}", expected_output="A concise grounded support answer.", agent=composer, context=[t1, t2])
    crew=Crew(agents=[retrieval, lookup, composer], tasks=[t1, t2, t3], process=Process.sequential, verbose=False)
    return crew.kickoff()
