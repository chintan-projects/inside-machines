## Step 1

WORD SCORING · STEP 1 OF 4

Start with the last layer’s result

The processed position is blue. Its completed result is [-2.33, 4.55]. A fixed output-scoring rule turns this pair into one score per possible next text piece.

last layer → [-2.33, 4.55] → one score per candidate

All values are rounded; arithmetic uses full precision. These are illustrative toy scores, not probabilities or measured language ability.

## Step 2

WORD SCORING · STEP 2 OF 4

One fixed direction per candidate

The toy declares these two-number scoring directions. They stay fixed while text is generated; they are not attention’s changing shares. Real models learn their output weights during training.

blue
[0.60, 0.50]
clear
[0.20, 0.50]
dark
[-0.30, 0.20]
and
[-0.50, 0.25]
.
[-0.30, 0.30]

All values are rounded; arithmetic uses full precision. These are illustrative toy scores, not probabilities or measured language ability.

## Step 3

WORD SCORING · STEP 3 OF 4

Multiply, then add

For each candidate, multiply matching coordinates of the result and that candidate’s direction; add the two products. This produces its score.

blue
[-2.33, 4.55] · [0.60, 0.50]
= -1.397 + 2.274 ≈ 0.88
clear
[-2.33, 4.55] · [0.20, 0.50]
= -0.466 + 2.274 ≈ 1.81
dark
[-2.33, 4.55] · [-0.30, 0.20]
= 0.699 + 0.910 ≈ 1.61
and
[-2.33, 4.55] · [-0.50, 0.25]
= 1.164 + 1.137 ≈ 2.30
.
[-2.33, 4.55] · [-0.30, 0.30]
= 0.699 + 1.365 ≈ 2.06

All values are rounded; arithmetic uses full precision. These are illustrative toy scores, not probabilities or measured language ability.

## Step 4

WORD SCORING · STEP 4 OF 4

Choose the largest score

This toy always chooses the largest score. Selection happens after the layers. The selected text still needs its own processing before another choice.

blue
score 0.88
clear
score 1.81
dark
score 1.61
and
score 2.30 ← highest
.
score 2.06

All values are rounded; arithmetic uses full precision. These are illustrative toy scores, not probabilities or measured language ability.