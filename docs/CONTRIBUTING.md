# Contributing to Puppet Engine

## Overview

Thank you for your interest in contributing to Puppet Engine! This document provides guidelines and information for contributors to help make the contribution process smooth and effective.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Git** for version control
- **GitHub account** for pull requests
- **Basic understanding** of async Python and AI/ML concepts

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/puppet-engine.git
   cd puppet-engine
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-username/puppet-engine.git
   ```

## Development Setup

### Environment Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure development environment**:
   ```env
   # Development settings
   ENVIRONMENT=development
   LOG_LEVEL=DEBUG
   DATABASE_URL=sqlite:///dev_puppet_engine.db
   
   # Test API keys (use fake/test keys for development)
   TWITTER_API_KEY=test_key
   TWITTER_API_SECRET=test_secret
   OPENAI_API_KEY=test_key
   ```

### Running the Application

```bash
# Development mode with auto-reload
python -m src.main --dev

# Run tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Code Style and Standards

### Python Style Guide

We follow **PEP 8** with some additional guidelines:

#### Code Formatting

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Double quotes for docstrings, single quotes for strings
- **Import order**: Standard library, third-party, local imports

#### Example

```python
"""Module for handling agent interactions."""

import asyncio
from typing import Dict, List, Optional

import aiohttp
from pydantic import BaseModel

from src.core.models import Agent, Memory
from src.utils.observability import logger


class InteractionHandler:
    """Handles agent interactions and responses."""

    def __init__(self, config: Dict[str, any]) -> None:
        """Initialize the interaction handler.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def process_interaction(
        self, agent: Agent, message: str
    ) -> Optional[str]:
        """Process an interaction for an agent.

        Args:
            agent: The agent to process for
            message: The message to process

        Returns:
            Optional response message
        """
        try:
            # Process the interaction
            response = await self._generate_response(agent, message)
            logger.info(f"Generated response for {agent.id}")
            return response
        except Exception as e:
            logger.error(f"Error processing interaction: {e}")
            return None

    async def _generate_response(self, agent: Agent, message: str) -> str:
        """Generate a response for the agent.

        Args:
            agent: The agent
            message: The input message

        Returns:
            Generated response
        """
        # Implementation here
        pass
```

### Type Hints

- **Use type hints** for all function parameters and return values
- **Use Optional[]** for parameters that can be None
- **Use Union[]** for parameters that can be multiple types
- **Use List[], Dict[], etc.** for collections

```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[Dict[str, any]], 
    config: Optional[Dict[str, any]] = None
) -> Union[str, None]:
    """Process data with optional configuration."""
    pass
```

### Async/Await

- **Use async/await** for all I/O operations
- **Use asyncio.gather()** for concurrent operations
- **Handle exceptions** properly in async functions

```python
async def process_multiple_agents(agents: List[Agent]) -> List[str]:
    """Process multiple agents concurrently."""
    try:
        tasks = [process_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    except Exception as e:
        logger.error(f"Error processing agents: {e}")
        return []
```

### Error Handling

- **Use specific exceptions** when possible
- **Log errors** with appropriate context
- **Don't catch and ignore** exceptions without logging

```python
class PuppetEngineError(Exception):
    """Base exception for Puppet Engine."""
    pass


class AgentNotFoundError(PuppetEngineError):
    """Raised when an agent is not found."""
    pass


async def get_agent(agent_id: str) -> Agent:
    """Get an agent by ID."""
    try:
        agent = await agent_store.get(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        return agent
    except AgentNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {agent_id}: {e}")
        raise PuppetEngineError(f"Failed to retrieve agent: {e}")
```

## Testing Guidelines

### Test Structure

Follow the existing test structure:

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
└── e2e/           # End-to-end tests for complete workflows
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.agent_manager import AgentManager


class TestAgentManager:
    """Test agent management functionality."""

    @pytest.mark.asyncio
    async def test_agent_creation(self, mock_memory_store, mock_llm_provider):
        """Test creating a new agent."""
        # Arrange
        manager = AgentManager({
            'memory_store': mock_memory_store,
            'default_llm_provider': mock_llm_provider,
            'event_engine': MagicMock()
        })
        config = {
            "id": "test-agent",
            "name": "Test Agent",
            "personality": {"traits": ["curious"]}
        }

        # Act
        agent_id = await manager.create_agent(config)

        # Assert
        assert agent_id == "test-agent"
        assert "test-agent" in manager.agents
        assert manager.agents["test-agent"].name == "Test Agent"

    @pytest.mark.asyncio
    async def test_agent_not_found(self, agent_manager):
        """Test error handling when agent is not found."""
        # Act & Assert
        with pytest.raises(AgentNotFoundError):
            await agent_manager.get_agent("nonexistent-agent")
```

#### Integration Tests

```python
import pytest
from src.agents.agent_manager import AgentManager
from src.memory.sqlite_store import SQLiteStore


class TestAgentIntegration:
    """Test agent integration with other components."""

    @pytest.mark.asyncio
    async def test_agent_memory_integration(self, settings):
        """Test agent memory integration."""
        # Arrange
        memory_store = SQLiteStore(settings)
        await memory_store.initialize()
        
        manager = AgentManager({
            'memory_store': memory_store,
            'default_llm_provider': FakeLLMProvider(),
            'event_engine': MagicMock()
        })

        # Act
        agent_id = await manager.create_agent(sample_config)
        await manager.add_memory(agent_id, "Test memory", "recent")
        memories = await memory_store.get_memories(agent_id, limit=10)

        # Assert
        assert len(memories) >= 1
        assert any("Test memory" in m.content for m in memories)
```

### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test one thing per test** method
4. **Use appropriate assertions** for the data type
5. **Mock external dependencies** to isolate the unit under test
6. **Test both success and failure** scenarios
7. **Use parametrized tests** for testing multiple scenarios

```python
@pytest.mark.parametrize("input_data,expected", [
    ({"valid": True}, True),
    ({"valid": False}, False),
    ({}, False),
])
def test_validation_logic(input_data, expected):
    """Test validation logic with different inputs."""
    result = validate_data(input_data)
    assert result == expected
```

### Test Coverage

- **Aim for 90%+ coverage** for new code
- **Run coverage reports** before submitting PRs
- **Focus on critical paths** and edge cases

```bash
# Run coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   pytest
   pytest --cov=src --cov-report=html
   ```

2. **Run linting**:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   ```

3. **Update documentation** if needed

4. **Test your changes** thoroughly

### Creating a Pull Request

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request** on GitHub

### Pull Request Template

Use the following template for pull requests:

```markdown
## Description

Brief description of the changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings generated
- [ ] Tests added that prove fix is effective or feature works

## Additional Notes

Any additional information or context.
```

### Commit Message Guidelines

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

#### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples

```
feat(agents): add support for custom personality traits

fix(api): resolve memory leak in agent manager

docs(readme): update installation instructions

test(memory): add comprehensive test coverage for SQLite store
```

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment information**:
   - Operating system
   - Python version
   - Puppet Engine version
   - Dependencies versions
5. **Error messages** and stack traces
6. **Screenshots** if applicable

### Issue Template

```markdown
## Bug Description

[Clear description of the bug]

## Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior

[What you expected to happen]

## Actual Behavior

[What actually happened]

## Environment

- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Puppet Engine Version: [e.g., 1.0.0]
- Dependencies: [List relevant package versions]

## Error Messages

```
[Paste error messages here]
```

## Additional Context

[Any additional information that might be helpful]
```

## Feature Requests

### Before Submitting

1. **Check existing issues** to avoid duplicates
2. **Search documentation** to see if feature already exists
3. **Consider the scope** and impact of the feature

### Feature Request Template

```markdown
## Feature Description

[Clear description of the feature]

## Use Case

[Explain why this feature is needed and how it would be used]

## Proposed Implementation

[Optional: Describe how you think this could be implemented]

## Alternatives Considered

[Optional: Describe any alternatives you've considered]

## Additional Context

[Any additional information that might be helpful]
```

## Documentation

### Documentation Standards

- **Write clear, concise documentation**
- **Use proper Markdown formatting**
- **Include code examples** where appropriate
- **Keep documentation up to date** with code changes

### Documentation Structure

```
docs/
├── README.md              # Main project documentation
├── ARCHITECTURE.md        # System architecture
├── API_REFERENCE.md       # API documentation
├── DEPLOYMENT.md          # Deployment guide
├── TESTING.md             # Testing guide
├── CONTRIBUTING.md        # This file
└── examples/              # Code examples
```

### Writing Documentation

#### Code Examples

```markdown
## Example Usage

Here's how to use the new feature:

```python
from src.agents.agent_manager import AgentManager

# Create agent manager
manager = AgentManager(config)

# Create an agent
agent_config = {
    "id": "my-agent",
    "name": "My Agent",
    "personality": {
        "traits": ["curious", "helpful"],
        "values": ["knowledge", "community"]
    }
}

agent_id = await manager.create_agent(agent_config)
```

#### API Documentation

```markdown
## POST /agents/{agent_id}/post

Trigger a manual post from an agent.

### Parameters

- `agent_id` (path): The unique identifier of the agent

### Request Body

```json
{
  "context": {
    "topic": "artificial intelligence",
    "mood": "excited"
  },
  "force": false
}
```

### Response

```json
{
  "status": "success",
  "data": {
    "post_id": "1234567890123456789",
    "content": "Generated tweet content...",
    "posted_at": "2024-12-19T10:35:00Z"
  }
}
```
```

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** and considerate of others
- **Use inclusive language** in comments and documentation
- **Give constructive feedback** on pull requests
- **Help newcomers** learn and contribute

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Documentation**: For improving docs

### Getting Help

If you need help:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Ask in GitHub Discussions**
4. **Create a new issue** if needed

### Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

## Development Workflow

### Daily Workflow

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make changes** and commit:
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature
   ```

### Code Review Process

1. **Self-review** your changes before submitting
2. **Request reviews** from maintainers
3. **Address feedback** promptly
4. **Merge only after approval**

### Release Process

1. **Create release branch** from main
2. **Update version** and changelog
3. **Run full test suite**
4. **Create release** on GitHub
5. **Deploy** to production

## Tools and Resources

### Development Tools

- **VS Code**: Recommended editor with Python extensions
- **PyCharm**: Alternative IDE with good Python support
- **Jupyter Notebooks**: For experimentation and testing

### Useful Commands

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Check for security issues
bandit -r src/

# Type checking
mypy src/
```

### Learning Resources

- **Python Async**: [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **Pytest**: [pytest documentation](https://docs.pytest.org/)
- **SQLite**: [SQLite documentation](https://www.sqlite.org/docs.html)

## Questions?

If you have questions about contributing:

1. **Check this document** first
2. **Search existing issues** and discussions
3. **Ask in GitHub Discussions**
4. **Contact maintainers** if needed

Thank you for contributing to Puppet Engine! 🚀 