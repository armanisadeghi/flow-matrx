import { useQueryClient } from "@tanstack/react-query";
import { runsApi } from "../../api/runs";
import type { RunStatus } from "@shared/types/run";

interface RunControlsProps {
  runId: string;
  status: RunStatus;
}

export default function RunControls({ runId, status }: RunControlsProps) {
  const queryClient = useQueryClient();

  const handleCancel = async () => {
    await runsApi.cancel(runId);
    // Invalidate so run history and any other consumers pick up the final state.
    await queryClient.invalidateQueries({ queryKey: ["run", runId] });
    await queryClient.invalidateQueries({ queryKey: ["runs"] });
  };

  const handleResume = async () => {
    await runsApi.resume(runId);
  };

  return (
    <div className="flex gap-2">
      {status === "paused" && (
        <button
          type="button"
          onClick={handleResume}
          className="px-3 py-1 text-sm bg-green-600 rounded hover:bg-green-500"
        >
          Resume
        </button>
      )}
      {(status === "running" || status === "paused") && (
        <button
          type="button"
          onClick={handleCancel}
          className="px-3 py-1 text-sm bg-red-700 rounded hover:bg-red-600"
        >
          Cancel
        </button>
      )}
    </div>
  );
}
