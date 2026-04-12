import { Check } from "lucide-react";

const STEPS = ["Basics", "Configuration", "Guardrails", "Evaluation", "Review"];

interface StepIndicatorProps {
  current: number;
}

export default function StepIndicator({ current }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      {STEPS.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <div key={label} className="flex items-center gap-2">
            {i > 0 && (
              <div
                className={`h-px w-8 ${done ? "bg-zinc-900" : "bg-zinc-200"}`}
              />
            )}
            <div className="flex items-center gap-2">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ${
                  done
                    ? "bg-zinc-900 text-white"
                    : active
                      ? "border-2 border-zinc-900 text-zinc-900"
                      : "bg-zinc-100 text-zinc-400"
                }`}
              >
                {done ? <Check className="w-3.5 h-3.5" /> : i + 1}
              </div>
              <span
                className={`text-sm hidden sm:inline ${
                  active
                    ? "font-medium text-zinc-900"
                    : done
                      ? "text-zinc-600"
                      : "text-zinc-400"
                }`}
              >
                {label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
