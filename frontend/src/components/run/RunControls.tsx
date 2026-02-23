import { runsApi } from "../../api/runs";
import type { Run } from "@shared/types/run";

interface RunControlsProps {
  run: Run;
}

export default function RunControls({ run }: RunControlsProps) {
  const handleCancel = async () => {
    await runsApi.cancel(run.id);
  };

  const handleResume = async () => {
    await runsApi.resume(run.id);
  };

  return (
    <div className="flex gap-2">
      {run.status === "paused" && (
        <button
          onClick={handleResume}
          className="px-3 py-1 text-sm bg-green-600 rounded hover:bg-green-500"
        >
          Resume
        </button>
      )}
      {(run.status === "running" || run.status === "paused") && (
        <button
          onClick={handleCancel}
          className="px-3 py-1 text-sm bg-red-700 rounded hover:bg-red-600"
        >
          Cancel
        </button>
      )}
    </div>
  );
}
