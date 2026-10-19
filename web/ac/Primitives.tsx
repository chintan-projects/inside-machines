import type { ReactElement, ReactNode } from "react";
import { box, OUTDOOR, path, project, wire } from "./geometry";
import type { Flat, Origin, Point } from "./geometry";

const metal = ["#e5e7e2", "#c2cac6", "#a2afac"];
export function Block({
  at,
  size,
  origin = OUTDOOR,
  tones = metal,
}: {
  readonly at: Point;
  readonly size: Point;
  readonly origin?: Origin;
  readonly tones?: readonly string[];
}): ReactElement {
  const b = box(at, size, origin);
  return (
    <g stroke="#586864" strokeWidth="1" strokeLinejoin="round">
      <path d={b.front} fill={tones[1]} />
      <path d={b.side} fill={tones[2]} />
      <path d={b.top} fill={tones[0]} />
    </g>
  );
}
export function Tube({
  points,
  origin = OUTDOOR,
  color = "#b97a55",
  width = 5,
}: {
  readonly points: readonly Point[];
  readonly origin?: Origin;
  readonly color?: string;
  readonly width?: number;
}): ReactElement {
  const d = wire(points, origin);
  return (
    <g fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d={d} stroke="#6e6052" strokeWidth={width + 2} />
      <path d={d} stroke={color} strokeWidth={width} />
      <path d={d} stroke="white" strokeOpacity=".3" strokeWidth="1" />
    </g>
  );
}
export function Cylinder({
  x,
  y,
  z,
  r,
  h,
}: {
  readonly x: number;
  readonly y: number;
  readonly z: number;
  readonly r: number;
  readonly h: number;
}): ReactElement {
  const top = project([x, y, z + h], OUTDOOR),
    bottom = project([x, y, z], OUTDOOR),
    rx = r * 1.216,
    ry = r * 0.608;
  return (
    <g stroke="#4e625e" strokeWidth="1">
      <path
        d={`M${top[0] - rx},${top[1]}v${h}a${rx},${ry} 0 0 0 ${rx * 2},0v${-h}`}
        fill="url(#ac-compressor-metal)"
      />
      <ellipse cx={bottom[0]} cy={bottom[1]} rx={rx} ry={ry} fill="none" />
      <ellipse cx={top[0]} cy={top[1]} rx={rx} ry={ry} fill="#80958e" />
      <ellipse cx={top[0]} cy={top[1] - 2} rx={rx * 0.8} ry={ry * 0.8} fill="#a0b0a6" stroke="none" />
    </g>
  );
}
export function Screw({
  at,
  origin = OUTDOOR,
}: {
  readonly at: Point;
  readonly origin?: Origin;
}): ReactElement {
  const [x, y] = project(at, origin);
  return (
    <g stroke="#69716a" strokeWidth=".8">
      <ellipse cx={x} cy={y} rx="2.5" ry="1.5" fill="#e8e6dc" />
      <path d={`M${x - 1.5},${y}h3`} />
    </g>
  );
}
export function Fan({
  origin,
  at,
  r,
}: {
  readonly origin: Origin;
  readonly at: Point;
  readonly r: number;
}): ReactElement {
  const [x, y] = project(at, origin);
  return (
    <g transform={`matrix(.86 .43 0 1 ${x} ${y})`}>
      <circle r={r + 5} fill="#ced6cf" stroke="#677a72" strokeWidth="2" />
      <circle r={r} fill="#344d4c" />
      <g className="ac-fan-rotor">
        {[0, 120, 240].map((a) => (
          <path
            key={a}
            transform={`rotate(${a})`}
            d={`M0,-5 C${r * 0.2},${-r * 0.9} ${r * 0.85},${-r * 0.9} ${r * 0.9},${-r * 0.3} Q${r * 0.7},${r * 0.2} 5,7Z`}
            fill="#a7bbb0"
            stroke="#546e63"
            strokeWidth="1"
          />
        ))}
      </g>
      <g fill="none" stroke="#d3d9cf" strokeWidth="1.2">
        {[0.4, 0.65, 0.9].map((f) => (
          <circle key={f} r={r * f} />
        ))}
        {[0, 45, 90, 135].map((a) => (
          <path key={a} transform={`rotate(${a})`} d={`M${-r},0H${r}`} />
        ))}
      </g>
      <circle r="8" fill="#d4dbd0" stroke="#6c8175" />
    </g>
  );
}
export function Part({
  id,
  focus,
  onSelect,
  children,
}: {
  readonly id: string;
  readonly focus: string;
  readonly onSelect: (id: string) => void;
  readonly children: ReactNode;
}): ReactElement {
  return (
    <g className={`ac-hardware-part ${focus === id ? "ac-part-active" : ""}`} onClick={() => onSelect(id)}>
      {children}
    </g>
  );
}
export function Callout({
  x,
  y,
  to,
  title,
  sub,
  active,
  onClick,
  large = false,
}: {
  readonly x: number;
  readonly y: number;
  readonly to: readonly [number, number];
  readonly title: string;
  readonly sub: string;
  readonly active: boolean;
  readonly onClick: () => void;
  readonly large?: boolean;
}): ReactElement {
  return (
    <g
      className={`ac-callout ${active ? "ac-callout-active" : ""}`}
      role="button"
      tabIndex={0}
      aria-label={`Inspect ${title}`}
      aria-pressed={active}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <path
        d={`M${x + 10},${y + 17}V${y + 26}L${to[0]},${to[1]}`}
        fill="none"
        stroke={active ? "#286e75" : "#a7afa7"}
        strokeWidth="1.2"
      />
      <circle cx={to[0]} cy={to[1]} r="3" fill={active ? "#286e75" : "#9ba69e"} />
      <rect
        x={x - 9}
        y={y - (large ? 46 : 26)}
        width={title.length * (large ? 26 : 13) + 22}
        height={large ? 58 : 54}
        rx="4"
        fill="#f3f2ee"
        fillOpacity=".95"
      />
      <text x={x} y={y - 5} fontSize={large ? 48 : 24} fontWeight="600" fill={active ? "#21626b" : "#354740"}>
        {title}
      </text>
      {!large && (
        <text x={x} y={y + 20} fontSize="18" fill="#58675e">
          {sub}
        </text>
      )}
    </g>
  );
}
export function Flow({
  points,
  color,
  active,
}: {
  readonly points: readonly Flat[];
  readonly color: string;
  readonly active: boolean;
}): ReactElement {
  const d = path(points),
    a = points[0],
    b = points[1],
    x = (a[0] + b[0]) / 2,
    y = (a[1] + b[1]) / 2,
    angle = (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI;
  return (
    <g fill="none" strokeLinecap="round" strokeLinejoin="round">
      <path d={d} stroke="#7e8e85" strokeWidth="10" />
      <path d={d} stroke={color} strokeWidth="7" />
      {active && <path className="ac-flow" d={d} stroke="#fffaf2" strokeWidth="2.5" strokeDasharray="2 27" />}
      <path
        d="M-5,-4L0,0L-5,4"
        transform={`translate(${x} ${y}) rotate(${angle})`}
        stroke="#f8fbef"
        strokeWidth="2"
      />
    </g>
  );
}
