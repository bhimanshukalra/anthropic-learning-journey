# Topic Definitions

**Goal:** Define every AI topic from the absolute basics — skipping nothing — so this file becomes a strong foundation that can be referenced time and again. Quick, to-the-point definitions, ordered from basics upward.

## Study Batches (temporary — remove when all covered)

- [x] **Batch 1 — Absolute basics:** what is a model, parameters/weights, training loop, training vs. inference, tokens, next-token prediction
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

### Model Training (How ML Learns Rules from Data)

Training loop: (1) predict on a training example, (2) a loss function scores how wrong the prediction was, (3) backpropagation computes which direction each weight should move to reduce the error, (4) gradient descent nudges every weight a tiny step that way. Repeated over millions of examples, the weights collectively encode patterns no human wrote. Consequences: learned rules are not human-readable (black box), and the model is only as good as its training data. LLMs train on one simple task — predict the next token — at massive scale.

### Training vs. Inference

A model's two separate phases. Training = learning: weights are adjusted; happens once, at the lab, on massive GPU clusters. Inference = using: weights are frozen; every chat/API call is inference, and nothing is learned during it. This is why models have a knowledge cutoff and don't remember past conversations — usage never changes the weights.

### Token

Models compute on numbers, not words, so text is chopped into tokens — chunks of ~3–4 English characters (common words = 1 token; rare words split into pieces) — each mapped to a number via a fixed vocabulary table. Rule of thumb: 1,000 tokens ≈ 750 words. Tokens are the unit of API pricing, context-window limits, and generation speed.

### Next-Token Prediction

The single thing an LLM does: given a sequence of tokens, output a probability for every vocabulary token being the next one. Generation = pick a token from those probabilities, append it, feed the sequence back in, repeat. Consequences: output is generated sequentially (hence streaming) and sampled from probabilities (hence non-deterministic output; controlled by temperature).

## Agentic Patterns

### Evaluator-Optimizer Pattern

An agentic workflow where one LLM (optimizer) generates a response and a second LLM (evaluator) critiques it against defined criteria, looping feedback back for revision until the criteria are met.
