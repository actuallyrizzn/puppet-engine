from typing import List, Optional, Dict, Any
import json
from ..types import Agent, Personality, StyleGuide, Relationship
from ..memory.database import db

class AgentManager:
    def __init__(self):
        self._agents: Dict[int, Agent] = {}
    
    async def create_agent(
        self,
        name: str,
        personality: Personality,
        style_guide: StyleGuide,
        mood: Optional[str] = None
    ) -> Agent:
        """Create a new agent and store it in the database."""
        async with db.connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO agents (
                    name, personality_name, personality_description, personality_traits,
                    style_guide_tone, style_guide_language, style_guide_quirks, mood
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    personality.name,
                    personality.description,
                    json.dumps(personality.traits),
                    style_guide.tone,
                    style_guide.language,
                    json.dumps(style_guide.quirks) if style_guide.quirks else None,
                    mood
                )
            )
            agent_id = cursor.lastrowid
            
            agent = Agent(
                id=agent_id,
                name=name,
                personality=personality,
                style_guide=style_guide,
                mood=mood,
                relationships=[]
            )
            
            self._agents[agent_id] = agent
            return agent
    
    async def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        if agent_id in self._agents:
            return self._agents[agent_id]
        
        async with db.connect() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM agents WHERE id = ?",
                (agent_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            agent = Agent(
                id=row["id"],
                name=row["name"],
                personality=Personality(
                    name=row["personality_name"],
                    description=row["personality_description"],
                    traits=json.loads(row["personality_traits"])
                ),
                style_guide=StyleGuide(
                    tone=row["style_guide_tone"],
                    language=row["style_guide_language"],
                    quirks=json.loads(row["style_guide_quirks"]) if row["style_guide_quirks"] else None
                ),
                mood=row["mood"],
                relationships=await self._get_agent_relationships(agent_id)
            )
            
            self._agents[agent_id] = agent
            return agent
    
    async def list_agents(self) -> List[Agent]:
        """List all agents."""
        async with db.connect() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT id FROM agents")
            rows = await cursor.fetchall()
            
            agents = []
            for row in rows:
                agent = await self.get_agent(row["id"])
                if agent:
                    agents.append(agent)
            
            return agents
    
    async def update_agent_mood(self, agent_id: int, mood: str) -> Optional[Agent]:
        """Update an agent's mood."""
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        
        async with db.connect() as conn:
            await conn.execute(
                "UPDATE agents SET mood = ? WHERE id = ?",
                (mood, agent_id)
            )
            await conn.commit()
        
        agent.mood = mood
        return agent
    
    async def _get_agent_relationships(self, agent_id: int) -> List[Relationship]:
        """Get all relationships for an agent."""
        relationships = await db.get_agent_relationships(agent_id)
        return [
            Relationship(
                agent_id=r["agent_id"],
                target_id=r["target_id"],
                relationship_type=r["relationship_type"],
                strength=r["strength"]
            )
            for r in relationships
        ]
    
    async def add_relationship(
        self,
        agent_id: int,
        target_id: int,
        relationship_type: str,
        strength: float
    ) -> Optional[Relationship]:
        """Add a relationship between two agents."""
        agent = await self.get_agent(agent_id)
        target = await self.get_agent(target_id)
        
        if not agent or not target:
            return None
        
        relationship = Relationship(
            agent_id=agent_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength
        )
        
        await db.add_relationship(
            agent_id=agent_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength
        )
        
        if agent.relationships is None:
            agent.relationships = []
        agent.relationships.append(relationship)
        
        return relationship

# Global agent manager instance
agent_manager = AgentManager() 