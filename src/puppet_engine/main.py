"""
Puppet Engine - Main Entry Point

Autonomous AI agent framework for deploying persistent characters on Twitter.
"""

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
        "puppet-engine.log",
        rotation="1 day",
        retention="7 days",
        level=settings.log_level
    )
    
    logger.info("Starting Puppet Engine Python...")
    
    # Initialize API server
    api_server = APIServer(settings)
    
    # Start server
    uvicorn.run(
        api_server.app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    asyncio.run(main()) 