import { create } from "zustand";
import type { Run, StepRun } from "@shared/types/run";

interface RunState {
  activeRun: Run | null;
  stepRunsById: Record<string, StepRun>;

  setActiveRun: (run: Run | null) => void;
  updateStepRun: (stepRun: StepRun) => void;
  reset: () => void;
}

export const useRunStore = create<RunState>((set) => ({
  activeRun: null,
  stepRunsById: {},

  setActiveRun: (run) => set({ activeRun: run }),
  updateStepRun: (stepRun) =>
    set((state) => ({
      stepRunsById: { ...state.stepRunsById, [stepRun.id]: stepRun },
    })),
  reset: () => set({ activeRun: null, stepRunsById: {} }),
}));
