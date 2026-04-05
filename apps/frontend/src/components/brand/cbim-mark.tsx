'use client';

interface CBIMMarkProps {
  size?: number;
  color?: string;
  weight?: number | null;
  animate?: boolean;
  delay?: number;
}

export function CBIMMark({
  size = 100,
  color = "#10B981",
  weight = null,
  animate = false,
  delay = 0
}: CBIMMarkProps) {
  const s = size;
  const w = weight || s * 0.08;
  const r = s * 0.36;
  const cx = s * 0.48;
  const cy = s * 0.5;
  const gapDeg = 65;
  const toRad = (d: number) => (Math.PI / 180) * d;
  const startDeg = -gapDeg / 2;
  const endDeg = 360 - gapDeg / 2;
  const x1 = cx + r * Math.cos(toRad(startDeg));
  const y1 = cy + r * Math.sin(toRad(startDeg));
  const x2 = cx + r * Math.cos(toRad(endDeg));
  const y2 = cy + r * Math.sin(toRad(endDeg));
  const arcPath = `M${x1.toFixed(1)},${y1.toFixed(1)} A${r},${r} 0 1,1 ${x2.toFixed(1)},${y2.toFixed(1)}`;
  const arcLen = 2 * Math.PI * r * ((360 - gapDeg) / 360);
  const bx = cx + r * 0.2;
  const bTop = cy - r - s * 0.08;
  const bBot = cy - r * 0.3;
  const lineLen = bBot - bTop;

  return (
    <svg viewBox={`0 0 ${s} ${s}`} width={s} height={s} style={{ display: 'block' }}>
      {animate && (
        <style>{`
          @keyframes arcDraw { to { stroke-dashoffset: 0; } }
          @keyframes lineDraw { to { stroke-dashoffset: 0; } }
        `}</style>
      )}
      <path
        d={arcPath}
        fill="none"
        stroke={color}
        strokeWidth={w}
        strokeLinecap="round"
        style={animate ? {
          strokeDasharray: arcLen + 10,
          strokeDashoffset: arcLen + 10,
          animation: `arcDraw 0.8s cubic-bezier(0.4,0,0.2,1) ${delay}s forwards`
        } : {}}
      />
      <line
        x1={bx}
        y1={bTop}
        x2={bx}
        y2={bBot}
        stroke={color}
        strokeWidth={w * 0.6}
        strokeLinecap="round"
        style={animate ? {
          strokeDasharray: lineLen + 5,
          strokeDashoffset: lineLen + 5,
          animation: `lineDraw 0.4s cubic-bezier(0.4,0,0.2,1) ${delay + 0.5}s forwards`
        } : {}}
      />
    </svg>
  );
}
