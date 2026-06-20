"""Serve the Clause-Finder as an A2A agent.

Run it:
    uvicorn claimmate.a2a_server:app --host localhost --port 8001

Then point the orchestrator at it:
    set CLAIMMATE_CLAUSE_FINDER_URL=http://localhost:8001
The agent card is published at /.well-known/agent-card.json
"""
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .clause_finder import clause_finder_agent

app = to_a2a(clause_finder_agent, host="localhost", port=8001)
