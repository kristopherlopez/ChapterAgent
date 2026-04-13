import { HealthStatus } from "@/lib/types";
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

const config: Record<HealthStatus, { icon: typeof CheckCircle2; label: string; className: string }> = {
  pass: {
    icon: CheckCircle2,
    label: "PASS",
    className: "text-emerald-700 bg-emerald-50 border-emerald-200",
  },
  warn: {
    icon: AlertTriangle,
    label: "WARN",
    className: "text-amber-700 bg-amber-50 border-amber-200",
  },
  fail: {
    icon: XCircle,
    label: "FAIL",
    className: "text-red-700 bg-red-50 border-red-200",
  },
  pending: {
    icon: Clock,
    label: "PENDING",
    className: "text-zinc-500 bg-zinc-50 border-zinc-200",
  },
};

export default function HealthBadge({ status }: { status: HealthStatus }) {
  const { icon: Icon, label, className } = config[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${className}`}
    >
      <Icon className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}
