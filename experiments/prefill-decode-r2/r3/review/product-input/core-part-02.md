blue
THE PAST CANNOT READ BLUE
Old layer-1 inputs → same old results
↓ same inputs to layer 2
Same old prepared data at layer 2

Appending blue changes none of the inputs those earlier positions could read.

SAVED PREPARATION · SEPARATE FROM LAYER OUTPUTS
Layer 1
The
match · take
sky
match · take
is
match · take
blue
not prepared
Layer 2
The
match · take
sky
match · take
is
match · take
blue
not prepared

Match: helps set how much to read. Take: supplies the numbers to combine.

4 / 5 · The next choice

Use earlier work instead of doing it again

Earlier positions cannot read blue. Their layer-one results stay unchanged; those unchanged results feed layer two. So their prepared reading data stays valid at both layers.

Saved preparation still gets read at every layer.

## second_choice 2

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

At each layer: read the three old saved pairs plus blue’s own new pair, then update blue’s working numbers.

SAVED PREPARATION · SEPARATE FROM LAYER OUTPUTS
Layer 1
The
match · take
sky
match · take
is
match · take
blue
match · take
Layer 2
The
match · take
sky
match · take
is
match · take
blue
match · take

Match: helps set how much to read. Take: supplies the numbers to combine.

4 / 5 · The next choice

Use earlier work instead of doing it again

Keep that earlier reading data. Now process only blue. At each layer, it prepares its own lists and reads the saved past plus itself.

Saved preparation still gets read at every layer.

## second_choice 3

MODEL INPUT
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
↓
OUTSIDE THE LAYERS · COMPARE SCORES

Final result at blue → one score per candidate.

blue
0.88
clear
1.81
dark
1.61
and
2.30
.
2.06

and wins. Chosen text; not yet processed.

Scores are not probabilities. This toy always picks the largest.

4 / 5 · The next choice

Use earlier work instead of doing it again

Blue’s finished result scores the candidates for slot five. Choose the highest-scoring piece outside the layers. This chosen piece has not been processed yet.

Saved preparation still gets read at every layer.

## whole 1

REPLAY THE PASS THAT PROCESSES BLUE
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
slot 5
?
Old preparation kept

The · sky · is saved at each layer.

Blue’s entry is empty.

Preparation cleared

No entries saved at either layer.

The input text stays.

What must each copy process?

Input text stays. Saved preparation is cleared. No next word has been chosen in this replay yet.

Make a prediction, then use “Show the next step”.

5 / 5 · What caching saves

Replay the same pass: keep or clear

Rewind to before blue’s pass. One copy keeps the three old pairs at each layer; another clears them. Both have The sky is blue. Predict what each must process.

Same fixed toy, same text, same choices. We count positions, not seconds.

## whole 2

ONE FIXED EXAMPLE
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
slot 5
?

Preparation kept

1

Blue through both layers.
Reads saved past.

Preparation cleared

4

The + sky + is + blue
through both layers.

Positions processed through the whole model in pass 2. Not a timing or speed ratio.

Keep preparation
Clear & replay
SAVED PREPARATION · SEPARATE FROM LAYER OUTPUTS
Layer 1
The
match · take
sky
match · take
is
match · take
blue
match · take
Layer 2
The
match · take
sky
match · take
is
match · take
blue
match · take

Match: helps set how much to read. Take: supplies the numbers to combine.

One new position processed. Same choice: and.

5 / 5 · What caching saves

Replay the same pass: keep or clear

The empty copy processes all four positions to rebuild preparation. The kept copy processes only blue. Both still read the past. These counts are not timings.

Same fixed toy, same text, same choices. We count positions, not seconds.

## whole 3

REPLAY THE SAME PASS
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
Kept
1

position through both layers

Cleared
4

positions through both layers

Same text → same preparation → same choice: and.

Blue reads the past in both cases. Counts are positions, not time.

5 / 5 · What caching saves

Replay the same pass: keep or clear

Rebuilding from the same text gives the same preparation. Our deterministic toy chooses the same continuation again. Saving earlier work changes the work, not this choice.

Same fixed toy, same text, same choices. We count positions, not seconds.

## whole 4

REPLAY THE SAME PASS
slot 1
The
slot 2
sky
slot 3
is
slot 4
blue
KV CACHE · SEPARATE FROM LAYER OUTPUTS
Layer 1
The
key · value
sky
key · value
is
key · value
blue
key · value
Layer 2
The
key · value
sky
key · value
is
key · value
blue
key · value

Match: helps set how much to read. Take: supplies the numbers to combine.

These are input-derived reading lists, kept separately at each layer.

“How the cache is read” shows the different jobs of keys and values with actual numbers.

5 / 5 · What caching saves

Replay the same pass: keep or clear

These prepared lists are called keys and values. Keeping them is a KV cache: separate at each layer. It saves reprocessing the past, not reading it.

Same fixed toy, same text, same choices. We count positions, not seconds.