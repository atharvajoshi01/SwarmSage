"""
Shared test fixtures for SwarmSage backend tests.
"""

import os
import sys
import json
import tempfile
import shutil
import pytest

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set required env vars before importing app modules
os.environ.setdefault('LLM_API_KEY', 'test-key-not-real')
os.environ.setdefault('LLM_BASE_URL', 'https://api.openai.com/v1')
os.environ.setdefault('LLM_MODEL_NAME', 'gpt-4o-mini')
os.environ.setdefault('ZEP_API_KEY', 'test-zep-key-not-real')
os.environ.setdefault('FLASK_DEBUG', 'False')


@pytest.fixture
def app():
    """Create a Flask test application."""
    from app import create_app
    from app.config import Config

    # Use a temporary upload folder
    tmp_dir = tempfile.mkdtemp(prefix='swarmsage_test_')
    Config.UPLOAD_FOLDER = tmp_dir
    Config.OASIS_SIMULATION_DATA_DIR = os.path.join(tmp_dir, 'simulations')

    test_app = create_app(Config)
    test_app.config['TESTING'] = True

    yield test_app

    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test files."""
    d = tempfile.mkdtemp(prefix='swarmsage_test_')
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_text():
    """Provide sample text content for testing."""
    return (
        "Dr. Alice Chen is a professor at Stanford University specializing in "
        "artificial intelligence. She collaborates with Dr. Bob Smith from MIT "
        "on a joint research project about multi-agent systems. Their paper was "
        "published in Nature in 2024. The project is funded by DARPA and aims "
        "to create autonomous agents that can simulate complex social dynamics. "
        "Alice leads a team of 15 graduate students, while Bob manages the "
        "computational infrastructure. They hold weekly meetings every Tuesday "
        "via video conference. The project has attracted attention from tech "
        "companies like Google and Meta, who have expressed interest in licensing "
        "the technology for social media simulation purposes."
    )


@pytest.fixture
def sample_txt_file(tmp_dir, sample_text):
    """Create a sample .txt file."""
    path = os.path.join(tmp_dir, 'sample.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    return path


@pytest.fixture
def sample_md_file(tmp_dir):
    """Create a sample .md file."""
    content = (
        "# Research Report\n\n"
        "## Summary\n"
        "This report covers the analysis of social media trends.\n\n"
        "## Key Findings\n"
        "- Agent-based models show promise for prediction\n"
        "- Swarm intelligence can model crowd behavior\n"
        "- Real-time simulation requires GPU acceleration\n"
    )
    path = os.path.join(tmp_dir, 'sample.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


@pytest.fixture
def sample_ontology():
    """Provide a sample ontology structure."""
    return {
        "entity_types": [
            {"name": "Person", "description": "A human individual"},
            {"name": "Organization", "description": "A company or institution"},
            {"name": "Project", "description": "A research or business project"},
            {"name": "Technology", "description": "A technology or tool"},
        ],
        "relationship_types": [
            {"name": "WORKS_AT", "source": "Person", "target": "Organization"},
            {"name": "COLLABORATES_WITH", "source": "Person", "target": "Person"},
            {"name": "FUNDS", "source": "Organization", "target": "Project"},
            {"name": "USES", "source": "Project", "target": "Technology"},
        ]
    }


@pytest.fixture
def sample_agent_profiles():
    """Provide sample OASIS agent profiles."""
    return [
        {
            "name": "Alice Chen",
            "bio": "AI professor at Stanford University",
            "persona": "An ambitious and meticulous AI researcher who values collaboration.",
            "age": 42,
            "gender": "female",
            "mbti": "INTJ",
            "profession": "Professor",
            "interests": ["AI", "multi-agent systems", "neural networks"],
            "twitter_followers": 5000,
            "twitter_following": 200,
            "twitter_posts_count": 150,
            "reddit_karma": 3000,
        },
        {
            "name": "Bob Smith",
            "bio": "Computational infrastructure lead at MIT",
            "persona": "A pragmatic engineer who focuses on scalable systems.",
            "age": 38,
            "gender": "male",
            "mbti": "ISTP",
            "profession": "Research Scientist",
            "interests": ["distributed systems", "GPU computing", "simulation"],
            "twitter_followers": 2000,
            "twitter_following": 300,
            "twitter_posts_count": 80,
            "reddit_karma": 1500,
        },
    ]


@pytest.fixture
def sample_simulation_config():
    """Provide a sample simulation configuration."""
    return {
        "time_config": {
            "total_rounds": 10,
            "time_per_round_hours": 1,
            "start_hour": 9,
        },
        "event_config": {
            "initial_posts": [
                {
                    "author": "Alice Chen",
                    "content": "Excited to announce our new multi-agent simulation paper!",
                    "platform": "twitter",
                }
            ],
            "hot_topics": ["AI research", "multi-agent systems"],
        },
        "agent_config": {
            "activity_levels": {"high": 0.3, "medium": 0.5, "low": 0.2},
            "sentiment_bias": 0.1,
        },
        "platform_config": {
            "twitter": {"viral_threshold": 10, "algorithm_weight": 0.7},
            "reddit": {"viral_threshold": 5, "algorithm_weight": 0.5},
        },
    }
