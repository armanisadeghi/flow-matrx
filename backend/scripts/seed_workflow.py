"""
Script 1 — Seed a real workflow into the database.

Run from backend/:
    uv run python scripts/seed_workflow.py

What it does:
    1. Connects to the real DB via matrx_orm (reads .env automatically)
    2. Grabs the first org + user it finds (you need at least one in the DB)
    3. Creates a 2-step workflow: HTTP fetch → transform
    4. Prints the workflow ID — paste it into scripts/run_workflow.py
"""

import asyncio

from matrx_utils import clear_terminal, vcprint

import app.bootstrap  # noqa: F401 — must be first: writes DB env vars before matrx_orm is imported
from app.db.custom import wf_core
from app.db.models import OrgManager, UserProfileManager

WORKFLOW_DEF = {
    "nodes": [
        {
            "id": "fetch",
            "type": "http_request",
            "position": {"x": 0, "y": 0},
            "data": {
                "label": "Fetch Todo",
                "config": {
                    "method": "GET",
                    "url": "https://jsonplaceholder.typicode.com/todos/1",
                },
            },
        },
        {
            "id": "extract",
            "type": "transform",
            "position": {"x": 0, "y": 200},
            "data": {
                "label": "Extract Fields",
                "config": {
                    "mapping": {
                        "title": "{{fetch.body.title}}",
                        "completed": "{{fetch.body.completed}}",
                        "user_id": "{{fetch.body.userId}}",
                    }
                },
            },
        },
    ],
    "edges": [
        {"id": "e1", "source": "fetch", "target": "extract"},
    ],
}


async def main() -> None:
    # --- Find an org and user to attach to -----------------------------------
    org_mgr = OrgManager()
    orgs = await org_mgr.load_items()
    if not orgs:
        print("ERROR: No rows in public.org. Create an org first.")
        return
    org_id = str(orgs[0].id)

    user_mgr = UserProfileManager()
    users = await user_mgr.load_items()
    if not users:
        print("ERROR: No rows in public.user_profile. Create a user profile first.")
        return
    user_id = str(users[0].id)

    print(f"Using org_id  : {org_id}")
    print(f"Using user_id : {user_id}")

    # --- Create the workflow --------------------------------------------------
    wf = await wf_core.create_workflow(
        org_id=org_id,
        user_id=user_id,
        name="Real Test — Fetch + Transform",
        description="Fetches a todo from JSONPlaceholder and extracts fields.",
        status="published",
        definition=WORKFLOW_DEF,
        input_schema={},
    )

    print("\nWorkflow created successfully!")
    print(f"  id          : {wf.id}")
    print(f"  name        : {wf.name}")
    print(f"  status      : {wf.status}")
    print("\nPaste this into scripts/run_workflow.py:")
    print(f'  WORKFLOW_ID = "{wf.id}"')
    print(f'  ORG_ID      = "{org_id}"')
    print(f'  USER_ID     = "{user_id}"')

    vcprint(wf, "[SEED WORKFLOW TEST] Main workflow created", color="cyan")


if __name__ == "__main__":
    import asyncio
    clear_terminal()
    asyncio.run(main())
