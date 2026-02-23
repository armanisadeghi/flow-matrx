import { useState } from "react";
import { useWorkflowStore } from "../../stores/workflowStore";

interface TemplateInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function TemplateInput({ value, onChange, placeholder }: TemplateInputProps) {
  const nodes = useWorkflowStore((s) => s.nodes);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const suggestions = nodes.map((n) => `{{${n.id}.output}}`);

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
        placeholder={placeholder}
        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
      />
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 bg-slate-800 border border-slate-600 rounded mt-1 z-10">
          {suggestions.map((s) => (
            <button
              key={s}
              className="block w-full text-left px-3 py-1.5 text-sm hover:bg-slate-700 font-mono"
              onMouseDown={() => onChange(value + s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
