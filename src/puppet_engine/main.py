seline Integration Tests for Puppet Engine Migration

This test suite captures the current Node.js behavior to ensure
the Python migration maintains functional parity.

import asyncio
import uvicorn
from fastapi import FastAPI
from loguru import logger

from .core.settings import Settings
from .api.server import APIServer


async def main():
    settings = Settings()
    
    # Configure logging
    logger.add(
        puppet-engine.log",
        rotation="1 day",
        retention="7 days",
        level=settings.log_level
    )
    
    logger.info("Starting Puppet Engine Python...")
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="Autonomous AI agent framework,
        version="20
    ) 
    # Initialize API server
    api_server = APIServer(settings)
    app.include_router(api_server.router)
    
    # Start server
    uvicorn.run(
        app,
        host=0.0.00,
        port=8000,
        log_level=settings.log_level.lower()
    )


if __name__ == __main__:
    asyncio.run(main()) 