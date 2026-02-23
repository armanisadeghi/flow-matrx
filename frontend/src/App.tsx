import { BrowserRouter, Route, Routes } from "react-router";
import WorkflowList from "./pages/WorkflowList";
import WorkflowBuilder from "./pages/WorkflowBuilder";
import RunHistory from "./pages/RunHistory";
import RunDetail from "./pages/RunDetail";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WorkflowList />} />
        <Route path="/workflows/:workflowId/edit" element={<WorkflowBuilder />} />
        <Route path="/workflows/:workflowId/runs" element={<RunHistory />} />
        <Route path="/runs/:runId" element={<RunDetail />} />
      </Routes>
    </BrowserRouter>
  );
}
