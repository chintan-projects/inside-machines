import type { ReactElement } from "react";
import { INDOOR, OUTDOOR, project, wire } from "./geometry";
import type { Point } from "./geometry";
import type { Placement } from "./story";
import { Block, Tube, Cylinder, Screw, Fan, Part, Callout, Flow } from "./Primitives";

const indoorCoil: Point[] = [];
for (let i = 0; i < 5; i++) {
  const z = 145 - i * 17;
  indoorCoil.push([i % 2 ? 222 : 12, 27, z], [i % 2 ? 12 : 222, 27, z]);
}
const outdoorCoil: Point[] = [];
for (let i = 0; i < 7; i++) {
  const z = 180 - i * 23;
  outdoorCoil.push([i % 2 ? 210 : 132, 19, z], [i % 2 ? 132 : 210, 19, z]);
}
const suction = [
  [382.7, 360.1],
  [480, 401],
  [585, 401],
  [642.6, 408],
] as const;
const liquid = [
  [884.3, 466.5],
  [884.3, 500],
  [780, 537],
  [486, 537],
  [450, 518],
] as const;
const cold = [
  [427, 518],
  [145, 518],
  [145, 345],
  [185, 320],
  [185, 225],
  [202.1, 201.8],
] as const;
export interface HardwareProps {
  readonly step: number;
  readonly focus: string;
  readonly running: boolean;
  readonly placement: Placement;
  readonly preview?: boolean;
  readonly compact?: boolean;
  readonly overview?: boolean;
  readonly onSelect: (id: string) => void;
}
export function Hardware({
  step,
  focus,
  running,
  placement,
  onSelect,
  compact = false,
  overview = false,
  preview = false,
}: HardwareProps): ReactElement {
  const all = step === 0 || step === 5;
  const whole = !compact || overview || all;
  const frame = whole
    ? "90 90 950 540"
    : step === 1
      ? "90 95 455 515"
      : step === 4
        ? "100 320 670 310"
        : "535 100 510 520";
  const large = compact && whole;
  return (
    <svg
      className={`ac-hardware ${running ? "ac-running" : ""} ${placement === "inside" ? "ac-both-inside" : ""} ${compact && whole ? "ac-overview" : ""} ${preview ? "ac-preview" : ""}`}
      viewBox={frame}
      role={preview ? "img" : "group"}
      aria-label="Cutaway of a split-system air conditioner with labeled coils, compressor and expansion valve"
    >
      <defs>
        <linearGradient id="ac-compressor-metal">
          <stop stopColor="#45655e" />
          <stop offset=".4" stopColor="#759387" />
          <stop offset=".8" stopColor="#5a796b" />
          <stop offset="1" stopColor="#3c5b53" />
        </linearGradient>
        <pattern id="ac-dot-grid" width="18" height="18" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r=".65" fill="#bfc7bc" />
        </pattern>
        <marker
          id="ac-arrow-heat"
          viewBox="0 0 10 10"
          refX="7"
          refY="5"
          markerWidth="7"
          markerHeight="7"
          orient="auto"
        >
          <path d="M0,0L9,5L0,10" fill="none" stroke="#cf7846" strokeWidth="1.4" />
        </marker>
        <marker
          id="ac-arrow-air"
          viewBox="0 0 10 10"
          refX="7"
          refY="5"
          markerWidth="5"
          markerHeight="5"
          orient="auto"
        >
          <path d="M0,0L9,5L0,10" fill="none" stroke="#6b9a9c" strokeWidth="1.4" />
        </marker>
      </defs>
      <rect x="25" y="70" width="1050" height="515" rx="10" fill="url(#ac-dot-grid)" opacity=".35" />
      <path
        className="ac-room-ground"
        d={placement === "inside" ? "M40 135H1040V595H40Z" : "M40 135H535V595H40Z"}
        fill={placement === "inside" ? "#eee1d1" : "#e5eae0"}
        opacity=".65"
      />
      <path
        d={placement === "inside" ? "M1040 100V590" : "M535 100V590"}
        stroke="#c3c9bc"
        strokeWidth="2"
        strokeDasharray="3 7"
      />
      <text x="130" y="115" className="ac-space-label">
        {placement === "inside" ? "Both units inside the same sealed room" : "Inside your room"}
      </text>
      {placement === "outside" && (
        <text x="580" y="115" className="ac-space-label">
          Outdoors
        </text>
      )}
      <ellipse cx="300" cy="436" rx="150" ry="21" fill="#536f64" opacity=".08" />
      <ellipse cx="772" cy="540" rx="145" ry="22" fill="#536f64" opacity=".09" />
      {/* Indoor back shell, mounting rails, end walls and exposed finned evaporator. */}
      <Block
        at={[-6, 0, 10]}
        size={[258, 10, 163]}
        origin={INDOOR}
        tones={["#f4f3e9", "#e3e6db", "#c2cec1"]}
      />
      <Block at={[-6, 0, 10]} size={[8, 67, 155]} origin={INDOOR} />
      <Block at={[244, 0, 10]} size={[8, 67, 155]} origin={INDOOR} />
      <Block at={[-6, 64, 163]} size={[258, 6, 7]} origin={INDOOR} />
      <Part id="evaporator" focus={focus} onSelect={onSelect}>
        <g className={step === 1 ? "ac-coil-cold" : ""}>
          {Array.from({ length: 32 }, (_, i) => (
            <Block
              key={i}
              at={[10 + i * 7, 15, 65]}
              size={[1.5, 21, 92]}
              origin={INDOOR}
              tones={["#d2e2dd", "#aac4ba", "#7c9d94"]}
            />
          ))}
          <Tube points={indoorCoil} origin={INDOOR} color={step === 1 ? "#3b939f" : "#7aafb1"} width={4} />
          {(step === 1 || all) && (
            <path
              className="ac-flow"
              d={wire(indoorCoil, INDOOR)}
              stroke="#e5ffff"
              strokeWidth="1.8"
              strokeDasharray="2 22"
              fill="none"
            />
          )}
        </g>
      </Part>
      <Block at={[7, 53, 20]} size={[231, 8, 17]} origin={INDOOR} tones={["#627d74", "#8ca79a", "#526e65"]} />
      {Array.from({ length: 25 }, (_, i) => (
        <path
          key={i}
          d={wire(
            [
              [12 + i * 9, 54, 22],
              [12 + i * 9, 61, 36],
            ],
            INDOOR,
          )}
          stroke="#b7cdc0"
          strokeWidth="2"
        />
      ))}
      <Block at={[-6, 64, 8]} size={[258, 6, 9]} origin={INDOOR} tones={["#e3e8dd", "#c2cfc0", "#a5b4a6"]} />
      {[0, 1, 2].map((i) => (
        <Block
          key={i}
          at={[4, 66 + i * 7, 7 - i * 3]}
          size={[238, 2, 2]}
          origin={INDOOR}
          tones={["#c4d0c2", "#a3b6a8", "#a3b6a8"]}
        />
      ))}
      {[0, 240].flatMap((x) =>
        [22, 156].map((z) => <Screw key={`${x}-${z}`} at={[x, 66, z]} origin={INDOOR} />),
      )}
      {/* Condenser: back plate and real fin ribs sit behind the fan and compressor. */}
      <Block at={[-9, -6, 2]} size={[245, 130, 8]} tones={["#dcded2", "#b4bfb1", "#9baa9a"]} />
      <Block at={[-9, -6, 10]} size={[245, 7, 200]} tones={["#efeee3", "#d9dfd1", "#adbba7"]} />
      <Block at={[229, 0, 10]} size={[7, 115, 200]} />
      <Part id="condenser" focus={focus} onSelect={onSelect}>
        {Array.from({ length: 25 }, (_, i) => (
          <Block
            key={i}
            at={[123 + i * 4.3, 7, 22]}
            size={[1, 13, 171]}
            tones={["#c8d3c3", "#99af9c", "#788f7f"]}
          />
        ))}
        <Tube points={outdoorCoil} color={step === 3 ? "#da8650" : "#bd8a60"} width={4} />
      </Part>
      <Block at={[2, 22, 12]} size={[91, 91, 5]} tones={["#a5b8a5", "#839a88", "#6b8473"]} />
      {[20, 90, 188, 222].map((x) => (
        <Block key={x} at={[x, 80, 0]} size={[12, 23, 5]} tones={["#859b86", "#5b755f", "#405c46"]} />
      ))}
      <Part id="compressor" focus={focus} onSelect={onSelect}>
        <Cylinder x={59} y={58} z={19} r={29} h={97} />
        <Tube
          points={[
            [59, 58, 116],
            [59, 58, 151],
            [132, 58, 151],
            [132, 19, 180],
          ]}
          color={step === 2 || step === 3 || all ? "#d0774d" : "#c28254"}
        />
        <Tube
          points={[
            [27, 58, 66],
            [5, 58, 66],
            [5, 95, 45],
          ]}
          color="#7a9c91"
        />
        <Block at={[37, 81, 76]} size={[34, 4, 24]} tones={["#526d58", "#3c5b4a", "#304937"]} />
      </Part>
      <path
        d={wire(
          [
            [58, 86, 78],
            [58, 111, 78],
            [184, 111, 78],
            [184, 106, 139],
          ],
          OUTDOOR,
        )}
        stroke="#454f47"
        strokeWidth="2.5"
        fill="none"
      />
      <Block at={[160, 85, 22]} size={[44, 29, 118]} tones={["#c4c5b5", "#c8d3bf", "#a3b397"]} />
      {Array.from({ length: 6 }, (_, i) => (
        <path
          key={i}
          d={wire(
            [
              [166, 115, 35 + i * 16],
              [196, 115, 35 + i * 16],
            ],
            OUTDOOR,
          )}
          stroke="#7f947a"
          strokeWidth="2"
        />
      ))}
      <g className="ac-fan-cage">
        <Block at={[102, 108, 27]} size={[124, 5, 146]} tones={["#d4dbca", "#b4c3ad", "#8b9f83"]} />
        <Fan origin={OUTDOOR} at={[163, 116, 103]} r={53} />
      </g>
      <Block at={[-9, 118, 10]} size={[6, 6, 190]} />
      <Block at={[230, 118, 10]} size={[6, 6, 190]} />
      <Block at={[-9, 118, 200]} size={[245, 6, 9]} />
      <Block at={[-9, 118, 10]} size={[245, 6, 9]} tones={["#d8ddcf", "#b1bfab", "#94a58d"]} />
      {[0, 222].flatMap((x) => [25, 190].map((z) => <Screw key={`${x}-${z}`} at={[x, 120, z]} />))}
      <Flow points={suction} color="#659a9e" active={all || step === 2} />
      <Flow points={liquid} color="#bc9460" active={all || step === 3 || step === 4} />
      <Flow points={cold} color="#4d939e" active={all || step === 1 || step === 4} />
      {/* Valve is an actual fitting in the return line, with two collars and a stem. */}
      <Part id="expansion" focus={focus} onSelect={onSelect}>
        <g transform="translate(438 518)">
          <rect x="-17" y="-8" width="34" height="16" rx="3" fill="#b8a075" stroke="#75674b" />
          <path d="M-4,-8V-20H4V-8" fill="#a6aba0" stroke="#637369" />
          <circle cy="-22" r="5" fill="#b9c7ba" stroke="#6b7e6c" />
          <path d="M-12,-12V12M12,-12V12" stroke="#8b7b53" strokeWidth="3" />
        </g>
      </Part>
      <g className={`ac-heat-path ${step === 1 || all ? "ac-heat-active" : ""}`}>
        <path d="M105 245C140 232 174 254 227 270" />
        <path d="M99 280C153 265 188 289 241 303" />
      </g>
      <g
        className={`ac-cool-air ${step === 1 || all ? "ac-air-active" : ""}`}
        fill="none"
        stroke="#6b9a9c"
        strokeWidth="3"
        markerEnd="url(#ac-arrow-air)"
      >
        <path d="M205 383C195 405 170 398 156 415" />
        <path d="M244 402C232 427 212 418 191 435" />
        <path d="M284 420C271 444 248 439 231 454" />
      </g>
      <g className={`ac-heat-path ${step === 3 || all ? "ac-heat-active" : ""}`}>
        <path
          d={
            placement === "inside" ? "M893 342C963 334 1000 422 904 487" : "M915 350C952 333 961 361 1000 340"
          }
        />
        <path
          d={
            placement === "inside" ? "M904 393C969 403 964 463 905 500" : "M921 387C956 374 982 403 1025 382"
          }
        />
      </g>
      {!preview && (!compact || whole || focus === "evaporator") && (
        <Callout
          large={large}
          x={large ? 90 : 126}
          y={145}
          to={project([90, 27, 130], INDOOR)}
          title="Indoor coil"
          sub="Evaporator · picks up heat"
          active={focus === "evaporator"}
          onClick={() => onSelect("evaporator")}
        />
      )}
      {!preview && (!compact || whole || focus === "condenser") && (
        <Callout
          large={large}
          x={702}
          y={155}
          to={project([180, 19, 178], OUTDOOR)}
          title="Outdoor coil"
          sub="Condenser · releases heat"
          active={focus === "condenser"}
          onClick={() => onSelect("condenser")}
        />
      )}
      {!preview && (!compact || whole || focus === "compressor") && (
        <Callout
          large={large}
          x={large ? 650 : 590}
          y={576}
          to={project([59, 58, 95], OUTDOOR)}
          title="Compressor"
          sub="Raises pressure and temperature"
          active={focus === "compressor"}
          onClick={() => onSelect("compressor")}
        />
      )}
      {!preview && (!compact || whole || focus === "expansion") && (
        <Callout
          large={large}
          x={large ? 120 : 300}
          y={576}
          to={[438, 518]}
          title="Expansion valve"
          sub="Makes a cold mixture"
          active={focus === "expansion"}
          onClick={() => onSelect("expansion")}
        />
      )}
      <g className="ac-inline-labels">
        <text x="100" y="328">
          Heat in
        </text>
        <text x="917" y="431">
          {placement === "inside" ? "Heat back in" : "Heat out"}
        </text>
        <text x="250" y="467">
          Cooler room air
        </text>
      </g>
    </svg>
  );
}
