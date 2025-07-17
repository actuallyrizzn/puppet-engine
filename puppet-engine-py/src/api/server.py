from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from ..core.settings import settings
from ..adapters.node_adapter import NodeAdapter
from typing import Optional, Dict, Any

class APIServer:
    def __init__(self, settings):
        self.app = FastAPI(
            title="Puppet Engine API",
            description="Autonomous AI agent management API",
            version="2.0.0"
        )
        self.settings = settings
        self.node_adapter = NodeAdapter(settings)
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

        @self.app.api_route("/node/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_to_node(request: Request, path: str):
            method = request.method
            data: Optional[Dict[str, Any]] = await request.json() if method in ("POST", "PUT") else None
            try:
                result = await self.node_adapter.forward_request(method, f"/{path}", data)
                return result
            except Exception as e:
                raise HTTPException(status_code=502, detail=str(e))

    def _setup_observability(self):
        Instrumentator().instrument(self.app).expose(self.app)

# Entrypoint for running the API
app = APIServer(settings).app 