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
        # Parse CORS allowlist from settings (comma-separated string)
        allowlist_str = getattr(self.settings, "cors_allow_origins", None)
        allowlist = []
        if allowlist_str:
            allowlist = [origin.strip() for origin in allowlist_str.split(",") if origin.strip()]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowlist,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "ok"}

        @self.app.get("/config/cors")
        async def cors_config():
            allowlist_str = getattr(self.settings, "cors_allow_origins", None)
            allowlist = []
            if allowlist_str:
                allowlist = [origin.strip() for origin in allowlist_str.split(",") if origin.strip()]
            return {"allow_origins": allowlist}

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
        # Metrics
        Instrumentator().instrument(self.app).expose(self.app)
        # Tracing (env-gated)
        from ..utils.observability import setup_observability
        setup_observability(
            self.app,
            service_name="puppet-api",
            enable_tracing=bool(getattr(self.settings, "enable_tracing", False)),
            otlp_endpoint=getattr(self.settings, "otlp_endpoint", None),
            enable_console_tracing=bool(getattr(self.settings, "enable_console_tracing", False)),
        )

# Entrypoint for running the API
app = APIServer(settings).app 