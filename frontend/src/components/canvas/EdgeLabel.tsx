interface EdgeLabelProps {
  label: string;
  x: number;
  y: number;
}

export default function EdgeLabel({ label, x, y }: EdgeLabelProps) {
  return (
    <div
      style={{ transform: `translate(-50%, -50%) translate(${x}px,${y}px)` }}
      className="absolute pointer-events-none text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded"
    >
      {label}
    </div>
  );
}
