interface ConnectionIndicatorProps {
  connected: boolean;
}

export default function ConnectionIndicator({ connected }: ConnectionIndicatorProps) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-400">
      <span
        className={`inline-block w-2 h-2 rounded-full ${
          connected ? "bg-green-400 shadow-[0_0_6px_1px_rgba(74,222,128,0.6)]" : "bg-slate-600"
        }`}
      />
      {connected ? "live" : "connecting..."}
    </div>
  );
}
