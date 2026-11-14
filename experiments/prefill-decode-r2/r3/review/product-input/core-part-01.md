## tasks 1

ONE FIXED EXAMPLE
slot 1
The
slot 2
sky
slot 3
is
slot 4
?
EACH POSITION AIMS ONE SLOT AHEAD
The
→
slot 2
Already supplied: sky
sky
→
slot 3
Already supplied: is
is
→
slot 4
First blank to fill

These arrows show assigned tasks. They do not claim the toy predicted the supplied text.

1 / 5 · Next-slot tasks

One position, one next-slot task

Our prompt has three text pieces, called tokens: The, sky, is. Each position helps fill the slot right after it.

The prompt is supplied text. One position’s result targets one next slot.

## tasks 2

ONE FIXED EXAMPLE
slot 1
The
slot 2
sky
slot 3
is
slot 4
?
EACH POSITION AIMS ONE SLOT AHEAD
The
→
slot 2
Already supplied: sky
sky
→
slot 3
Already supplied: is
is
→
slot 4
First blank to fill

These arrows show assigned tasks. They do not claim the toy predicted the supplied text.

1 / 5 · Next-slot tasks

One position, one next-slot task

Two of those slots are already filled by your text: sky follows The, and is follows sky.

The prompt is supplied text. One position’s result targets one next slot.

## tasks 3

ONE FIXED EXAMPLE
slot 1
The
slot 2
sky
slot 3
is
slot 4
?
EACH POSITION AIMS ONE SLOT AHEAD
The
→
slot 2
Already supplied: sky
sky
→
slot 3
Already supplied: is
is
→
slot 4
First blank to fill

These arrows show assigned tasks. They do not claim the toy predicted the supplied text.

1 / 5 · Next-slot tasks

One position, one next-slot task

Only the last position, is, points at a blank: slot four.

The prompt is supplied text. One position’s result targets one next slot.

## first_choice 1

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
A LAYER IS ONE PROCESSING STAGE
Read this position + its allowed past
↓
Update this position’s working numbers

The numbers change; words are chosen after all the layers.

2 / 5 · The first choice

Build a result. Then choose.

The model works on numbers for each text piece. A layer is one stage: read this position and the past, then update this position’s working numbers.

Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.

## first_choice 2

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
THE AT ONE LAYER
The’s layer input
→ Prepare two lists used to read this position.
↓ read + update working numbers
Finished working result

The prepared reading data and finished result are different objects.

2 / 5 · The first choice

Build a result. Then choose.

To read a position, the layer first prepares two lists from that position’s input. This reading data is separate from its finished working result.

Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.

## first_choice 3

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
ONE PASS THROUGH THE MODEL
Input: The · sky · is
↓
Layer 1
3 positions
↓ then
Layer 2
3 positions

Each layer makes its own reading data from its inputs. Finished results feed the next layer; prepared reading data stays beside its own layer.

2 / 5 · The first choice

Build a result. Then choose.

Known positions run together inside a layer. Their finished results become the next layer’s inputs. The next layer prepares its own reading data.

Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.

## first_choice 4

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
↓
OUTSIDE THE LAYERS · COMPARE SCORES

Final result at is → one score per candidate.

blue
3.00
clear
2.04
dark
-0.10
and
-0.43
.
0.21

blue wins. Chosen text; not yet processed.

Scores are not probabilities. This toy always picks the largest.

2 / 5 · The first choice

Build a result. Then choose.

The final result at is gives a score for each possible next piece. Our fixed toy’s highest score is blue. Choose blue outside the layers.

Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.

## first_choice 5

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
CHOSEN AFTER THE LAYERS
blue
chosen · no result of its own yet
The layers processed is. Blue came out of the choosing step afterward.

2 / 5 · The first choice

Build a result. Then choose.

The layers processed is, not the blue they just chose. Blue has no result of its own yet.

Matching lists set the shares. Reading lists supply what gets combined. Word choice comes afterward.

## feed_back 1

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
EACH POSITION AIMS ONE SLOT AHEAD
The
→
slot 2
Already supplied: sky
sky
→
slot 3
Already supplied: is
is
→
slot 4
Already supplied: blue
blue
→
slot 5
First blank to fill

These arrows show assigned tasks. They do not claim the toy predicted the supplied text.

3 / 5 · Back in as input

The choice becomes the next input

Put blue back in as input. Its position targets slot five. The earlier positions targeted slots two, three, and four; none could read the later blue.

Text visible on the page and preparation inside the model are different states.

## feed_back 2

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
ONE PASS THROUGH THE MODEL
Input: blue
↓
Layer 1
1 position
↓ then
Layer 2
1 position

A new pass starts with blue. No following word has been chosen yet.

3 / 5 · Back in as input

The choice becomes the next input

Blue must now pass through the layers to build the result for slot five. Choosing blue did not do this work.

Text visible on the page and preparation inside the model are different states.

## second_choice 1

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
slot 4
