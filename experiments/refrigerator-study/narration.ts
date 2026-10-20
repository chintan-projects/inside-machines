/** Single authored scripts for narration, captions and reduced-motion checkpoints. */
import type { NarrationPlan } from '../visual-studio/contracts.ts';
export const refrigeratorCore: NarrationPlan = {
  id: 'refrigerator-r1-core-audio', duration: 104, cues: [
    { start: 0, end: 10, still: 2, text: 'A refrigerator keeps food cold by moving heat out of its cabinet. The warmth does not disappear; it goes into the kitchen.' },
    { start: 10, end: 22, still: 15, text: 'Inside, a coil carries refrigerant colder than the cabinet air. Heat moves from the warmer air, through the metal wall, into this fluid.' },
    { start: 22, end: 34, still: 27, text: 'At low pressure, some of that cold liquid boils. Turning liquid into vapor takes energy, so the refrigerant carries heat away from the cabinet.' },
    { start: 34, end: 49, still: 36.9, text: 'The compressor draws in vapor and uses electrical work to squeeze it. Pressure and temperature rise. This cutaway shows one piston design.' },
    { start: 49, end: 63, still: 55, text: 'The hotter refrigerant enters the outside coil. Because it is warmer than the kitchen air, heat leaves, and vapor condenses back into liquid.' },
    { start: 63, end: 77, still: 69, text: 'Liquid passes through a very narrow tube into the low-pressure side. Some flashes into vapor; the remaining cold mixture returns to the inside coil.' },
    { start: 77, end: 92, still: 84, text: 'Follow the loop: absorb heat inside, add work, release heat outside, then reduce pressure. Different parts do these jobs together while the compressor runs.' },
    { start: 92, end: 104, still: 97, text: 'Insulation slows heat returning to the cabinet. The refrigerator moves that heat back out. Its warm side releases the removed heat plus the work added.' },
  ],
};
export const refrigeratorEnergy: NarrationPlan = {
  id: 'refrigerator-r1-energy-audio', duration: 68, cues: [
    { start: 0, end: 10, still: 3, text: 'Why is the back warm? Keep track of energy entering and leaving the cooling loop. Start with the cabinet separate from the room.' },
    { start: 10, end: 24, still: 17, text: 'Here is an accounting example: three units of heat removed, plus one unit of work, means four units released. These numbers are not measured refrigerator performance.' },
    { start: 24, end: 38, still: 30, text: 'Now leave the door open. Both sides exchange heat with the same room. Taking three units out and putting four back leaves one extra unit in the room.' },
    { start: 38, end: 52, still: 44, text: 'That extra energy comes from the electrical work. A cool patch near the open door does not mean the kitchen as a whole is being cooled.' },
    { start: 52, end: 68, still: 58, text: 'The cabinet boundary matters. A closed refrigerator can keep food cooler than its surroundings while its warm side releases heat. Opening a real door also changes the heat load; our fixed numbers only explain the accounting.' },
  ],
};
export const refrigeratorPhase: NarrationPlan = {
  id: 'refrigerator-r1-phase-audio', duration: 62, cues: [
    { start: 0, end: 11, still: 3, text: 'Water boiling in a pot looks very hot. Must every boiling liquid be hot compared with the room? Look closely at the fluid inside a refrigerator.' },
    { start: 11, end: 24, still: 16, text: 'In the cold coil, low pressure lets refrigerant boil at a low temperature. Heat entering from the warmer cabinet supplies energy for liquid to become vapor.' },
    { start: 24, end: 37, still: 29, text: 'Compare the same fluid at the same chosen cold temperature, but at higher pressure. In this comparison it stays liquid because its boiling point is now higher.' },
    { start: 37, end: 49, still: 42, text: 'These are two assumed conditions, not a simulation of changing pressure. The actual boiling temperatures depend on the refrigerant and its pressure.' },
    { start: 49, end: 62, still: 55, text: 'Liquid can still absorb heat and warm without boiling. Phase change is one way to take in energy. The complete refrigerator keeps restoring the conditions for that process.' },
  ],
};
export const refrigeratorNarrations = [refrigeratorCore, refrigeratorEnergy, refrigeratorPhase];
