"""
Script 2 — Create a run and execute a workflow end-to-end against the real DB.

Run from backend/:
    uv run python scripts/run_workflow.py

Fill in the three IDs printed by scripts/seed_workflow.py before running.
"""

import asyncio
import json

from matrx_utils import clear_terminal, vcprint

import app.bootstrap  # noqa: F401 — must be first, configures matrx_orm
from app.db.custom import wf_core
from app.engine.executor import WorkflowEngine


def _section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


async def main(workflow_id: str, org_id: str, user_id: str) -> None:
    # --- Create a run --------------------------------------------------------
    _section("1. Creating run")
    run = await wf_core.create_run(
        {
            "workflow_id": workflow_id,
            "org_id": org_id,
            "user_id": user_id,
            "status": "pending",
            "trigger_type": "manual",
            "input": {"triggered_by": "run_workflow.py"},
            "context": {},
        }
    )

    vcprint(run, "[RUN WORKFLOW TEST] Run created", color="cyan")

    run_id = str(run.id)
    print(f"  run_id : {run_id}")
    print(f"  status : {run.status}")

    # --- Execute it -----------------------------------------------------------
    _section("2. Executing")
    engine = WorkflowEngine()
    await engine.execute_run(run_id)
    print("  execute_run() returned")

    # --- Read back the final run state ---------------------------------------
    _section("3. Final run state")
    final = await wf_core.get_run(run_id)
    vcprint(final, "[RUN WORKFLOW TEST] Run final state", color="blue")

    print(f"  status       : {final.status}")
    if final.error:
        print(f"  error        : {final.error}")
    print(f"  context keys : {list(final.context.keys()) if final.context else []}")
    if final.context:
        print(f"\n  Full context:")
        print(json.dumps(dict(final.context), indent=4, default=str))

    # --- Step-by-step results ------------------------------------------------
    _section("4. Step runs")
    step_runs = await wf_core.get_step_runs({"run_id": run_id})
    vcprint(step_runs, "[RUN WORKFLOW TEST] Step runs", color="green")
    if not step_runs:
        print("  (none recorded)")
    for sr in step_runs:
        print(f"\n  [{sr.step_id}]")
        print(f"    type    : {sr.step_type}")
        print(f"    status  : {sr.status}")
        print(f"    attempt : {sr.attempt}")
        if sr.error:
            print(f"    error   : {sr.error}")
        if sr.output:
            print(f"    output  : {json.dumps(dict(sr.output), indent=6, default=str)}")

    # --- Event log -----------------------------------------------------------
    _section("5. Event log (in order)")
    events = await wf_core.get_run_events({"run_id": run_id})
    vcprint(events, "[RUN WORKFLOW TEST] Event log", color="yellow")
    if not events:
        print("  (none recorded)")
    for ev in events:
        step_tag = f"  [{ev.step_id}]" if ev.step_id else ""
        print(f"  {ev.event_type}{step_tag}")

    # --- Pass / Fail verdict -------------------------------------------------
    _section("Result")
    if final.status == "completed":
        print("  PASSED — workflow completed successfully")
    else:
        print(f"  FAILED — final status is {final.status!r}")


if __name__ == "__main__":
    import asyncio

    clear_terminal()
    WORKFLOW_ID = "c787a823-cc24-4f1a-bf38-4a32226c1285"
    ORG_ID = "1cd167ec-d211-4df7-99e9-83c12712fde7"
    USER_ID = "af2cd4cc-447a-43f0-8ce6-89f29903b25d"
    asyncio.run(main(workflow_id=WORKFLOW_ID, org_id=ORG_ID, user_id=USER_ID))
