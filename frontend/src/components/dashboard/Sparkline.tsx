import { HealthSnapshot } from "@/lib/types";

const statusToY: Record<string, number> = {
  pass: 4,
  warn: 12,
  fail: 20,
};

const statusToColor: Record<string, string> = {
  pass: "#059669",
  warn: "#d97706",
  fail: "#dc2626",
};

export default function Sparkline({ history }: { history: HealthSnapshot[] }) {
  const width = 110;
  const height = 24;
  const padding = 2;
  const usableWidth = width - padding * 2;
  const step = history.length > 1 ? usableWidth / (history.length - 1) : 0;

  const points = history.map((snap, i) => ({
    x: padding + i * step,
    y: statusToY[snap.status],
    status: snap.status,
  }));

  // Build polyline segments colored by status
  const segments: { x1: number; y1: number; x2: number; y2: number; color: string }[] = [];
  for (let i = 0; i < points.length - 1; i++) {
    segments.push({
      x1: points[i].x,
      y1: points[i].y,
      x2: points[i + 1].x,
      y2: points[i + 1].y,
      color: statusToColor[points[i + 1].status],
    });
  }

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="block"
      aria-label={`Health trend: ${history.length} data points`}
    >
      {/* Background bands */}
      <rect x={0} y={0} width={width} height={8} fill="#f0fdf4" opacity={0.5} />
      <rect x={0} y={8} width={width} height={8} fill="#fffbeb" opacity={0.5} />
      <rect x={0} y={16} width={width} height={8} fill="#fef2f2" opacity={0.5} />

      {/* Line segments */}
      {segments.map((seg, i) => (
        <line
          key={i}
          x1={seg.x1}
          y1={seg.y1}
          x2={seg.x2}
          y2={seg.y2}
          stroke={seg.color}
          strokeWidth={1.5}
          strokeLinecap="round"
        />
      ))}

    </svg>
  );
}
