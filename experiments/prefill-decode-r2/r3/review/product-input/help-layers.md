## Step 1

BLUE · LAYER 1 · STEP 1 OF 6

Start with the input numbers

In this toy, blue enters layer 1 as [-0.60, 0.90]. The token has been looked up as two numbers. The coordinates have no assigned meanings.

input [-0.60, 0.90] → layer 1

## Step 2

BLUE · LAYER 1 · STEP 2 OF 6

Decide how much to take from each position

Blue computes comparison numbers (a query). Compare them with each allowed position’s matching list (its key). Convert those scores to shares that add to 100%.

blue’s query = [-0.15, 0.90]
The
key [1.00, 0.50] → 20.1%
sky
key [0.00, 1.00] → 30.7%
is
key [0.60, 0.70] → 23.8%
blue
key [-0.60, 0.60] → 25.4%
How the shares are calculated

## Step 3

BLUE · LAYER 1 · STEP 3 OF 6

Take those shares of the reading lists

Each share multiplies that position’s reading list (its value). Add the contributions. This is attention: positions can contribute to blue’s result.

The
20.1% × [0.80, 0.00]
= [0.16, 0.00]
sky
30.7% × [0.00, 0.80]
= [0.00, 0.25]
is
23.8% × [0.48, 0.32]
= [0.11, 0.08]
blue
25.4% × [-0.48, 0.72]
= [-0.12, 0.18]
sum of contributions = [0.15, 0.50]

Displayed values are rounded; the calculation uses full precision.

## Step 4

BLUE · LAYER 1 · STEP 4 OF 6

Add the blend to blue’s input

Keep the original numbers and add the blend. This is an add-back, or residual. The reading step has now changed blue’s numbers.

[-0.60, 0.90] + [0.15, 0.50]
= [-0.45, 1.40]

## Step 5

BLUE · LAYER 1 · STEP 5 OF 6

Compute and add a local adjustment

A second operation reworks only blue’s current pair. It does not read other positions again: matrix → set negatives to zero → second matrix. Add its adjustment to the current pair. This is the feed-forward step, with another residual.

current [-0.45, 1.40]
first matrix → [-1.85, 1.18]
remove negatives → [0.00, 1.18]
second matrix → adjustment [0.00, 0.59]
current + adjustment → [-0.45, 2.00]

## Step 6

BLUE · LAYER 1 · STEP 6 OF 6

Send the changed numbers onward

Layer 1 is finished. Its output becomes layer 2’s input. Layer 2 repeats these jobs with a different fixed set of matrices.

layer 1 output [-0.45, 2.00]
↓
layer 2 input [-0.45, 2.00]

## Step 7

BLUE · LAYER 2 · STEP 1 OF 6

Start with the input numbers

In this toy, blue enters layer 2 as [-0.45, 2.00]. These are exactly layer 1’s finished output. The coordinates have no assigned meanings.

input [-0.45, 2.00] → layer 2

## Step 8

BLUE · LAYER 2 · STEP 2 OF 6

Decide how much to take from each position

Blue computes comparison numbers (a query). Compare them with each allowed position’s matching list (its key). Convert those scores to shares that add to 100%.

blue’s query = [1.77, -0.45]
The
key [2.48, -0.45] → 69.3%
sky
key [1.50, 2.20] → 8.8%
is
key [1.85, 1.16] → 19.0%
blue
key [0.55, 2.00] → 2.9%
How the shares are calculated

## Step 9

BLUE · LAYER 2 · STEP 3 OF 6

Take those shares of the reading lists

Each share multiplies that position’s reading list (its value). Add the contributions. This is attention: positions can contribute to blue’s result.

The
69.3% × [-0.36, 2.16]
= [-0.25, 1.50]
sky
8.8% × [1.76, 0.32]
= [0.16, 0.03]
is
19.0% × [0.93, 1.01]
= [0.18, 0.19]
blue
2.9% × [1.60, -0.36]
= [0.05, -0.01]
sum of contributions = [0.13, 1.71]

Displayed values are rounded; the calculation uses full precision.

## Step 10

BLUE · LAYER 2 · STEP 4 OF 6

Add the blend to blue’s input

Keep the original numbers and add the blend. This is an add-back, or residual. The reading step has now changed blue’s numbers.

[-0.45, 2.00] + [0.13, 1.71]
= [-0.32, 3.70]

## Step 11

BLUE · LAYER 2 · STEP 5 OF 6

Compute and add a local adjustment

A second operation reworks only blue’s current pair. It does not read other positions again: matrix → set negatives to zero → second matrix. Add its adjustment to the current pair. This is the feed-forward step, with another residual.

current [-0.32, 3.70]
first matrix → [1.69, 4.02]
remove negatives → [1.69, 4.02]
second matrix → adjustment [-2.01, 0.85]
current + adjustment → [-2.33, 4.55]

## Step 12

BLUE · LAYER 2 · STEP 6 OF 6

Send the changed numbers onward

After layer 2, these numbers score the output candidates. Choosing the next text piece still happens outside the layers.

layer 2 output [-2.33, 4.55]
↓
score candidates → choose and