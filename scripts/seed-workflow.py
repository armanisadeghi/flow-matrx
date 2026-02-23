#!/usr/bin/env python3
"""Insert sample workflows into the database for development."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import asyncpg

SAMPLE_WORKFLOW = {
    "name": "Sample HTTP + LLM Workflow",
    "description": "Fetches data from an API and summarises it with an LLM.",
    "definition": {
        "nodes": [
            {
                "id": "fetch_data",
                "type": "http_request",
                "label": "Fetch Data",
                "config": {"method": "GET", "url": "https://api.github.com/repos/octocat/hello-world"},
                "position": {"x": 250, "y": 100},
            },
            {
                "id": "summarise",
                "type": "llm_call",
                "label": "Summarise",
                "config": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Summarise this repo data: {{fetch_data.body}}",
                        }
                    ],
                },
                "position": {"x": 250, "y": 250},
            },
        ],
        "edges": [{"id": "e1", "source": "fetch_data", "target": "summarise"}],
    },
}


async def seed():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flow_matrx")
    try:
        await conn.execute(
            """
            INSERT INTO workflows (name, description, definition)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
            """,
            SAMPLE_WORKFLOW["name"],
            SAMPLE_WORKFLOW["description"],
            json.dumps(SAMPLE_WORKFLOW["definition"]),
        )
        print("✅  Sample workflow inserted.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
