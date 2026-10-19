/** Presentation of the stored AC lesson; stage indices retain existing chat/narration meaning. */
export interface StoryStep {
  readonly short: string;
  readonly title: string;
  readonly copy: string;
  readonly next: string;
  readonly focus: string;
  readonly change: string;
}
export const story: readonly StoryStep[] = [
  {
    short: "Meet the two sides",
    title: "One loop connects the two sides.",
    copy: "The indoor unit picks up room heat. The outdoor unit lets it go. A fluid called refrigerant carries the heat between them in sealed pipes.",
    next: "Start at the indoor coil",
    focus: "evaporator",
    change: "Two air streams. One sealed loop.",
  },
  {
    short: "Pick up room heat",
    title: "First, take heat out of the room.",
    copy: "Room air passes over the cold indoor coil. Refrigerant inside absorbs the heat and boils into a gas. The same air returns to your room, cooler.",
    next: "Follow the refrigerant",
    focus: "evaporator",
    change: "Cold mixture → heat absorbed → vapor",
  },
  {
    short: "Give heat a push",
    title: "To let heat out, first make the refrigerant hotter.",
    copy: "The compressor uses electricity to squeeze the gas. Its pressure and temperature rise. Now the refrigerant is hotter than the air outside—even on a hot day.",
    next: "Let the heat escape",
    focus: "compressor",
    change: "Low-pressure vapor → compression → hotter vapor",
  },
  {
    short: "Release it outside",
    title: "Here is where the room’s heat leaves.",
    copy: "At the outdoor coil, heat passes from the hot refrigerant to outdoor air. A fan carries it away. As the refrigerant loses heat, it turns back into a liquid.",
    next: "Get ready to cool again",
    focus: "condenser",
    change: "Hot vapor → heat released → liquid",
  },
  {
    short: "Get cold again",
    title: "A small valve prepares the next trip.",
    copy: "Liquid squeezes through the expansion valve. The pressure drops, and some liquid flashes into gas. The resulting cold mixture can pick up room heat again.",
    next: "See the whole cycle",
    focus: "expansion",
    change: "High-pressure liquid → expansion → cold mixture",
  },
  {
    short: "Try the whole system",
    title: "So why does one unit have to be outside?",
    copy: "The outdoor coil releases the heat taken from your room, plus the energy added by the compressor. Try putting both units in the same sealed room.",
    next: "Start over",
    focus: "condenser",
    change: "Heat released = room heat removed + electrical work",
  },
];
export type Placement = "outside" | "inside";
export function roomOutcome(placement: Placement): { trend: string; explanation: string; cooling: boolean } {
  return placement === "outside"
    ? {
        trend: "The room loses heat",
        explanation:
          "The room’s heat leaves through the outdoor coil. The energy added by the compressor leaves there too.",
        cooling: true,
      }
    : {
        trend: "The room gains heat overall",
        explanation:
          "The indoor coil takes heat out of the air, but the other coil puts it all back—plus the compressor’s electrical work.",
        cooling: false,
      };
}
