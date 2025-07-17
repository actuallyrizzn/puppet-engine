from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from ..core.settings import settings
from typing import Optional, Dict, Any

class APIServer:
    def __init__(self, settings):
        self.app = FastAPI(
            title="Puppet Engine API",
            description="Autonomous AI agent management API",
            version="2.0.0"
        )
        self.settings = settings
        self._setup_middleware()
        self._setup_routes()
        self._setup_observability()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "ok"}

        @self.app.get("/agents")
        async def list_agents():
            # TODO: Implement agent listing
            return {"agents": []}

        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            # TODO: Implement agent details
            return {"agent_id": agent_id, "status": "active"}

        @self.app.post("/agents/{agent_id}/post")
        async def trigger_post(agent_id: str):
            # TODO: Implement manual post trigger
            return {"agent_id": agent_id, "action": "post_triggered"}

        @self.app.post("/agents/{agent_id}/trade")
        async def trigger_trade(agent_id: str):
            # TODO: Implement manual trade trigger
            return {"agent_id": agent_id, "action": "trade_triggered"}

    def _setup_observability(self):
        Instrumentator().instrument(self.app).expose(self.app)

# Entrypoint for running the API
app = APIServer(settings).app 