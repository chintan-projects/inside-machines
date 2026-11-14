## Step 1

SAVED PREPARATION · STEP 1 OF 6

Make preparation from a layer’s input

Take The in layer 1: input [1.00, 0.00]. Two fixed matrix operations make its matching list [1.00, 0.50] and its reading list [0.80, 0.00]. Save both. This branch happens before attention and the finished layer output.

Layer input → key / value → save in this layer’s tray.
Layer input + attention + local adjustment → finished output → next layer.

## Step 2

SAVED PREPARATION · STEP 2 OF 6

Keep preparation separate from the output

The’s completed layer-1 output is [2.70, -0.45]. That is not either saved list. The output goes to layer 2, which makes its own separate lists. Each layer needs its own tray.

Layer input → key / value → save in this layer’s tray.
Layer input + attention + local adjustment → finished output → next layer.

## Step 3

SAVED PREPARATION · STEP 3 OF 6

Use the matching list to set a share

Blue enters later. Its layer-1 query is [-0.15, 0.90]. Comparing this with all allowed matching lists sets the shares. The’s share is 20.1%. The matching list is called a key.

Blue query + saved keys → shares.
Shares × saved values → contributions → blend.
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

## Step 4

SAVED PREPARATION · STEP 4 OF 6

Take that share of the reading list

20.1% × The’s reading list [0.80, 0.00] = [0.16, 0.00]. Other positions contribute too; their contributions add. The reading list is called a value.

Blue query + saved keys → shares.
Shares × saved values → contributions → blend.
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

## Step 5

SAVED PREPARATION · STEP 5 OF 6

Reuse the same preparation, without losing the past

Before blue arrives, The, sky and is can only read themselves and earlier positions. They cannot read blue. Their inputs and prepared lists therefore do not change when blue is appended. Blue reads the saved lists and adds its own: it skips rebuilding the past, not reading it.

Original text → same preparation, whether rebuilt or kept.
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

## Step 6

SAVED PREPARATION · STEP 6 OF 6

An empty cache is more work, not lost text

Clear both layers’ trays. The original text still exists. Reprocess The, sky, is and blue to rebuild exactly the same lists. Both routes choose and in this fixed greedy toy. Four positions go through the whole model rather than one. This is not a fourfold speed claim.

Original text → same preparation, whether rebuilt or kept.
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