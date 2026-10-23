/** Reviewed local scripts. Each cue also supplies its sound-off text and static pose. */
import type { NarrationPlan } from '../visual-studio/contracts.ts';
export const coreNarration: NarrationPlan = {
  id: 'gpu-core-s3-audio-1', duration: 88, cues: [
    { start: 0, end: 10, still: 3, text: 'A GPU is a processor that performs calculations on data. Let’s follow one complete job: making a tiny picture brighter.' },
    { start: 10, end: 22, still: 15, text: 'Our picture has eight pixels. Each stores a small brightness number. These are toy values, not a real image format. Adding one to every value will make this picture brighter.' },
    { start: 22, end: 34, still: 27, text: 'The GPU does not choose the task. A program running on the CPU starts the work, specifying the calculation and the data. Here the instruction is simple: add one to each pixel.' },
    { start: 34, end: 46, still: 40, text: 'The pixel values are held in GPU memory. Calculations need those values available where they run. Memory stores the numbers; the chip performs the arithmetic. They have different jobs.' },
    { start: 46, end: 62, still: 58, text: 'Each pixel can be changed without another pixel’s answer. Our teaching model has four calculation slots, so four jobs run together, then four more. Every job reads its input, adds one, and produces a result.' },
    { start: 62, end: 74, still: 68, text: 'The results are written back to memory. The same eight pixels now have larger values. Displaying those values gives a brighter picture. We have followed the instruction all the way to a useful result.' },
    { start: 74, end: 88, still: 80, text: 'The complete loop: a program requests work, memory supplies data, the chip calculates, and results are stored for use. Similar independent work is a good fit. Dependencies and data supply can make calculations wait.' },
  ],
};
export const memoryNarration: NarrationPlan = {
  id: 'gpu-memory-s3-audio-1', duration: 60, cues: [
    { start: 0, end: 10, still: 3, text: 'Four slots need inputs to do useful calculations. Keep our eight pixel jobs and change only the data supply.' },
    { start: 10, end: 22, still: 14.5, text: 'First, our toy model makes one new input ready each round. One slot can work; the other three wait. Each delivered value is increased by one. Empty slots cannot calculate a missing input.' },
    { start: 22, end: 34, still: 23.5, text: 'Reset to the same inputs. Now supply four per round. The same four slots work together. The arithmetic is unchanged; only the supply of ready data has changed.' },
    { start: 34, end: 46, still: 39, text: 'Real GPUs also have caches, scheduling and overlapping transfers. Our model leaves those out. These rounds explain a constraint; they are not GPU clock cycles or measured speed.' },
    { start: 46, end: 60, still: 51, text: 'To use calculation capacity, useful work and its data must be ready. More slots alone cannot fix a limited supply. Return to the whole story, or explore how a matrix creates many related calculations.' },
  ],
};
export const matrixNarration: NarrationPlan = {
  id: 'gpu-matrix-s3-audio-1', duration: 76, cues: [
    { start: 0, end: 10, still: 4, text: 'From our add-one picture, take values one to four. Arrange them in a matrix: a number grid. B holds weights for combining them.' },
    { start: 10, end: 22, still: 16, text: 'Choose a row from A and a column from B. Pair their first numbers, then their second numbers. These pairs supply one output cell.' },
    { start: 22, end: 34, still: 30, text: 'Multiply each pair. One times two gives two. Two times one also gives two. These products came from the selected row and column.' },
    { start: 34, end: 44, still: 39, text: 'Add the products: two plus two equals four. Write four into the output cell. This calculation is called a dot product.' },
    { start: 44, end: 58, still: 50, text: 'Repeat for the other row and column combinations. Each output uses inputs, rather than another output’s answer. These calculations can run on available resources. Real implementations also organize data movement and reuse.' },
    { start: 58, end: 76, still: 66, text: 'Transformer models use matrix operations inside attention and other learned transformations. These tiny numbers are our example, not actual model weights. Matrix multiplication is one important ingredient, not a complete language model. Change a weight below and predict which output column will change.' },
  ],
};
