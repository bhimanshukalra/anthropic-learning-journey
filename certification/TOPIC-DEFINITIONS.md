# Topic Definitions

**Goal:** Define every AI topic from the absolute basics — skipping nothing — so this file becomes a strong foundation that can be referenced time and again. Quick, to-the-point definitions, ordered from basics upward.

## Study Batches (temporary — remove when all covered)

- [x] **Batch 1 — Absolute basics:** what is a model, parameters/weights, training loop, training vs. inference, tokens, next-token prediction
- [x] **Batch 1a — Network building blocks:** neuron, bias, activation function, layer, neural network
- [x] **Batch 1b — Training vocabulary:** loss function, gradient, learning rate, backpropagation, batch/epoch
- [x] **Batch 1c — Generation mechanics:** logits, softmax, greedy vs. sampling, autoregressive loop, stop tokens
- [ ] **Batch 2 — Generation controls:** context window, temperature, sampling (top-p), max tokens, why models hallucinate
- [ ] **Batch 3 — Inside the model:** embeddings, attention, transformer architecture (conceptual)
- [ ] **Batch 4 — How Claude-like models are made:** pre-training vs. fine-tuning vs. RLHF, system prompts, instruction-following
- [ ] **Batch 5 — Building on top:** prompts vs. API parameters, RAG, tool use / function calling

## Foundations

### Artificial Intelligence (AI)

The field of building computer systems that perform tasks normally requiring human intelligence — understanding language, recognizing images, making decisions, solving problems. Key distinction: traditional software follows explicit human-written rules; AI/ML systems infer their own rules from data, making them powerful on fuzzy, open-ended tasks but probabilistic rather than deterministic. Hierarchy: AI ⊃ Machine Learning (learns patterns from data) ⊃ Deep Learning (multi-layered neural networks) ⊃ Generative AI/LLMs (generate new content).

### Model

A mathematical function that maps an input to an output (like °C → °F conversion, but at enormous scale). An AI model's behavior is not hand-written — it is learned from data and stored entirely as a huge file of numbers (its parameters). Input goes in (as numbers), flows through the function, output comes out.

### Parameters (Weights)

The billions of adjustable numbers inside a model — like sliders on a giant mixing desk. Each one slightly influences how inputs combine into outputs; knowledge exists only in the combined setting of all of them, never in any single one. "An 8B model" = 8 billion parameters. Before training they are random and the model outputs gibberish.

### Neuron

A tiny score-calculator: take several input numbers (clues), multiply each by its importance level (weight), add them up, add a head start (bias), apply a cutoff rule (activation function), and pass the score on. Like rating a restaurant: (taste 9 × 0.7) + (price 6 × 0.2) + (distance 3 × 0.1) = 7.8. The ML twist: nobody sets the importance levels — training tunes them, and "billions of parameters" = billions of these importance levels.

### Bias

A learned number added after a neuron's weighted sum (the `+32` in C→F). It shifts the neuron's output up or down independently of its inputs — without it, zero inputs would force a zero output. Every neuron has one; biases count toward the parameter total alongside weights.

### Activation Function (Nonlinearity)

The "bend" applied to a neuron's result before passing it on (e.g., ReLU: negatives become 0, positives pass through). Essential because stacked linear functions collapse into one linear function — the bends are what let deep networks represent complex patterns. ReLU also lets neurons be "off" (output 0) for some inputs, so different neurons respond to different patterns.

### Layer

A group of neurons operating side by side on the same inputs, each with its own weights/bias, so each computes a different "opinion." Layers stack in sequence — "deep" learning = many layers. Intuition: early layers detect simple patterns (edges, spelling), later layers combine them into abstract ones (faces, meaning).

### Neural Network

The whole assembly: input → layer 1 → layer 2 → ... → output, where every connection is a weighted sum and every layer adds bends. It's the shape an AI model's function takes. Key split: humans design the architecture (the wiring); training learns the weights and biases (what flows through it).

### How Model, Neural Network, Training & ML Relate

A neural network is not how models are trained — it IS a model (one kind). Model = a machine with adjustable knobs (parameters). Neural network = one particular machine design (knobs arranged as neurons in layers). Training = the tuning process that sets the knobs from data (gradient descent). ML = the overall field of building knob-tuned-from-data machines. The machine and the tuning are separate choices: decision trees are ML models trained without neural networks or gradients; linear regression and neural networks both train via gradient descent. Rule: architecture = what is tuned; training = how it's tuned. Subset rule: every neural network is a model (even untrained, it's still an input→output function), but not every model is a neural network (linear regression, decision trees, k-nearest neighbors are models with no neurons/layers). "Model" names the role; "neural network" names one design for filling it.

### Model Training (How ML Learns Rules from Data)

Training loop: (1) predict on a training example, (2) a loss function scores how wrong the prediction was, (3) backpropagation computes which direction each weight should move to reduce the error, (4) gradient descent nudges every weight a tiny step that way. Repeated over millions of examples, the weights collectively encode patterns no human wrote. Consequences: learned rules are not human-readable (black box), and the model is only as good as its training data. LLMs train on one simple task — predict the next token — at massive scale.

### Loss Function

Turns "how wrong was the model's guess?" into a single number (e.g., squared difference between prediction and truth). Training's entire goal is to make this number small. For LLMs, the loss is essentially "how much probability did you put on the actual next token?" — high probability on the truth = tiny loss.

### Gradient

The slope under your feet in the loss landscape: for each knob (parameter), which direction (up/down) reduces the loss, and how steeply. Just a per-knob "which way is downhill" arrow — nothing more.

### Gradient Descent

The training algorithm: picture every knob-setting combination as a location and the loss as altitude — you're dropped at a random spot in fog and must find the valley. Feel the slope (gradient), take a small step downhill (update every knob), repeat millions of times. C→F example: predicting 100 when truth is 212 → gradient says "increase the weight, steeply" → nudge → slightly less wrong.

### Learning Rate

The step size in gradient descent. Too large → you leap over the valley and land higher (training oscillates/explodes); too small → training crawls. Set by humans, not learned — a "hyperparameter" (a setting about training itself).

### Backpropagation

The accounting trick that computes the gradient for billions of knobs in one backward sweep instead of testing each knob individually (which would need billions of reruns per step). Assembly-line intuition: the final product is wrong → the last station computes its share of blame and tells the previous station how wrong its input was → blame flows backward through all layers, each weight learning its personal correction. Math = chain rule; mechanism = blame flows backward. One training heartbeat: forward pass (predict) → backward pass (assign blame) → update (nudge every knob).

### Batch & Epoch

Batch = how many training examples are averaged before taking one gradient-descent step (steadier than reacting to single examples). Epoch = one full pass through the entire training dataset.

### Training vs. Inference

A model's two separate phases. Training = learning: weights are adjusted; happens once, at the lab, on massive GPU clusters. Inference = using: weights are frozen; every chat/API call is inference, and nothing is learned during it. This is why models have a knowledge cutoff and don't remember past conversations — usage never changes the weights.

### Token

Models compute on numbers, not words, so text is chopped into tokens — chunks of ~3–4 English characters (common words = 1 token; rare words split into pieces) — each mapped to a number via a fixed vocabulary table. Rule of thumb: 1,000 tokens ≈ 750 words. Tokens are the unit of API pricing, context-window limits, and generation speed.

### Next-Token Prediction (How Generation Works)

The single thing an LLM does. One forward pass: prompt tokens flow through the layers → final layer outputs a raw score per vocabulary token (~100k numbers, called logits) → softmax converts scores into probabilities summing to 100% (e.g., " Paris" 92%). Then pick one: greedy (always take the top — deterministic but repetitive) or sampling (weighted dice roll — the source of non-determinism; temperature reshapes the table before the roll). Append the chosen token, re-run the whole sequence for the next table, loop until a stop token or max-token limit — this loop is autoregressive generation. Consequences: streaming is literal (tokens are made one at a time), output tokens dominate latency (one full forward pass each), and hallucination isn't lying — the model always just samples its table, and there is no truth-checking step in the loop.

### LLM (Large Language Model)

A model — specifically a very large neural network — whose parameters were set using the ML training recipe (gradient descent on a loss), where the training task was next-token prediction over massive amounts of text. Every level of the stack applies: it's AI (performs intelligence-like tasks), ML (behavior learned from data, not hand-coded), deep learning (the model is a many-layered neural network), and a model (one big function: token numbers in → probability scores out). "Large" = billions of parameters; "Language" = the training data. Precise phrasing: an ML model trained by gradient descent — ML names the field, gradient descent + backpropagation is the mechanism.

## Agentic Patterns

### Evaluator-Optimizer Pattern

An agentic workflow where one LLM (optimizer) generates a response and a second LLM (evaluator) critiques it against defined criteria, looping feedback back for revision until the criteria are met.
