import type { ReactElement } from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { roomOutcome } from "./story";
import type { Placement } from "./story";

export function Experiment({
  placement,
  onChange,
}: {
  readonly placement: Placement;
  readonly onChange: (placement: Placement) => void;
}): ReactElement {
  const outcome = roomOutcome(placement);
  const choices = (
    <div className="ac-placement" role="group" aria-label="Outdoor unit location">
      <button aria-pressed={placement === "outside"} onClick={() => onChange("outside")}>
        Outside the room
      </button>
      <button aria-pressed={placement === "inside"} onClick={() => onChange("inside")}>
        Inside the same room
      </button>
    </div>
  );
  return (
    <section
      className={`ac-inline-experiment ${outcome.cooling ? "" : "ac-experiment-warm"}`}
      aria-label="Move the outdoor unit experiment"
    >
      {choices}
      <div className="ac-inline-outcome" role="status">
        {outcome.cooling ? <ArrowDownRight size={22} /> : <ArrowUpRight size={22} />}
        <strong>{outcome.trend}</strong>
        <p>{outcome.explanation}</p>
      </div>
    </section>
  );
}
