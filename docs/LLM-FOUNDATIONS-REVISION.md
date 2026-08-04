# LLM Foundations Revision

Use this before returning to Jay Alammar's transformer material. The goal is not to memorize every
mechanical detail; it is to make the main moving parts feel ordinary enough that the diagrams stop
being intimidating.

## Mental Model

An LLM is a neural network that reads a sequence of tokens, converts them into vectors, mixes
information across the sequence using attention, and predicts the next token.

The rough flow is:

```text
text -> tokens -> embeddings -> transformer blocks -> next-token probabilities
```

## 1. Tokens

Tokens are the chunks of text the model actually sees.

They can be whole words, parts of words, punctuation, spaces, or other text fragments. The model
does not directly read "sentences" the way humans do. It reads token IDs.

Example:

```text
"unbelievable" might become ["un", "believ", "able"]
```

The exact split depends on the tokenizer.

Key idea:

> Text is first converted into a list of token IDs. The model works with those IDs, not raw
> characters or words.

Self-check:

- Can I explain why a rare word may be split into multiple tokens?
- Can I explain why tokenization affects cost, context length, and model behavior?

Answers:

- Rare words may be split because the tokenizer has a limited vocabulary. Instead of storing every
  possible word, it stores common words and reusable word pieces.
- Tokenization affects cost because models are usually priced and limited by tokens, not characters
  or words. It affects context length because every token consumes space in the context window. It
  affects behavior because the model reasons over the token pieces it receives.

## 2. Embeddings

An embedding is a learned vector representation of a token.

The token ID itself is just a number. That number does not contain meaning. The embedding layer maps
each token ID into a vector with many dimensions, and the model learns useful relationships between
those vectors during training.

Simple intuition:

```text
token ID 1729 -> [0.12, -0.44, 0.88, ...]
```

Key idea:

> Embeddings turn discrete tokens into continuous vectors that a neural network can process.

Self-check:

- Can I explain why neural networks prefer vectors over text?
- Can I explain why similar words might end up with related embeddings?

Answers:

- Neural networks prefer vectors because their core operations are mathematical operations on
  numbers: matrix multiplication, addition, normalization, and nonlinear transformations.
- Similar words can end up with related embeddings because, during training, they appear in similar
  contexts and help predict similar surrounding tokens. The model learns to place them in related
  regions of vector space.

## 3. Why Vectors?

Neural networks are built from mathematical operations: matrix multiplication, addition, nonlinear
functions, and normalization. Text has to become numbers before those operations can happen.

Vectors are useful because they can encode many fuzzy properties at once. A token vector can carry
signals related to meaning, grammar, position, tone, topic, and possible next-token patterns.

Key idea:

> Vectors let the model represent meaning as directions and patterns in a high-dimensional space.

Self-check:

- Can I explain why "meaning" in an LLM is not stored as dictionary definitions?
- Can I explain why vector similarity can be useful for language?

Answers:

- Meaning is not stored as dictionary definitions because the model does not keep a lookup table of
  human-written explanations. It stores learned weights that transform vectors in useful ways.
- Vector similarity is useful because related words, phrases, or concepts often behave similarly in
  language. If their vectors are close or point in related directions, the model can reuse patterns
  learned from one context in another.

## 4. Context

Context is the sequence of tokens the model can currently look at.

When an LLM predicts the next token, it uses the previous tokens in the context window. It does not
have human memory unless information is present in the current context or retrieved through some
external system.

Example:

```text
The capital of France is
```

The model uses those previous tokens to assign high probability to likely next tokens such as
`Paris`.

Key idea:

> Context is the model's working input. The model predicts the next token based on the tokens it can
> attend to right now.

Self-check:

- Can I explain why longer context does not automatically mean better reasoning?
- Can I explain why missing context can make a model answer incorrectly?

Answers:

- Longer context does not automatically mean better reasoning because the model still has to find and
  use the relevant information. Extra context can add noise, distract attention, or make the task
  harder if the important details are buried.
- Missing context can make a model answer incorrectly because it predicts from what it can see. If
  the needed facts, constraints, or definitions are absent, it may rely on general patterns instead
  of the specific truth needed for the situation.

## 5. Attention

Attention lets each token gather information from other tokens in the context.

Without attention, each token would have a hard time knowing which other tokens matter. Attention
creates weighted connections between tokens, so the model can decide which earlier tokens are
important for interpreting the current one.

Example:

```text
The trophy would not fit in the suitcase because it was too large.
```

To understand `it`, the model needs to connect it more strongly to `trophy` than `suitcase`.

Key idea:

> Attention is the mechanism that lets tokens look at other tokens and pull in relevant information.

A useful shorthand:

- Query: what this token is looking for
- Key: what each token offers
- Value: the information that gets passed along
- Attention score: how much one token should listen to another

Self-check:

- Can I explain why attention is useful for pronouns, references, and long-distance dependencies?
- Can I explain query, key, and value without writing equations?

Answers:

- Attention is useful because a token often depends on another token that may be far away. Pronouns,
  references, repeated entities, and cause-effect relationships all require the model to connect
  different parts of the sequence.
- Query means "what this token is looking for." Key means "what each token can be matched by."
  Value means "the information that gets passed along if attention decides this token matters."

## 6. Why Transformers Replaced RNNs

Older sequence models like RNNs processed text mostly step by step. This made long-range
relationships harder to preserve and training harder to parallelize.

Transformers use attention to let tokens connect more directly across the sequence. This makes them
better at handling long-range dependencies and much easier to train efficiently on modern hardware.

Key idea:

> Transformers made language modeling more parallel, more scalable, and better at connecting
> information across a sequence.

Self-check:

- Can I explain why processing tokens one-by-one can be limiting?
- Can I explain why attention helps with distant words in a sentence?

Answers:

- Processing tokens one-by-one can be limiting because information has to travel through many steps.
  This makes long-range relationships harder to preserve and makes training less parallel.
- Attention helps with distant words because it lets a token connect directly to other relevant
  tokens in the sequence, even if they are far apart.

## 7. Training vs Inference

Training is when the model learns its weights.

During training, the model sees lots of text and repeatedly practices predicting the next token. When
it is wrong, the training process adjusts the weights so future predictions get slightly better.

Inference is when the trained model is used.

During inference, the weights are mostly fixed. The model receives a prompt, predicts the next token,
adds that token to the context, then predicts again.

```text
Training:  change the weights
Inference: use the weights
```

Key idea:

> Training creates the model's parameters. Inference uses those parameters to generate output.

Self-check:

- Can I explain why a model does not "learn" from a normal chat unless a separate training or memory
  system exists?
- Can I explain why generation happens one token at a time?

Answers:

- A normal chat usually does not change the model's weights. The model can use the current
  conversation as context, but that is different from training. Persistent learning needs a separate
  training, fine-tuning, or memory system.
- Generation happens one token at a time because the model's basic task is next-token prediction.
  After it chooses one token, that token is added to the context, and the model predicts the next one.

## Jay Alammar Reading Strategy

When returning to Jay Alammar, do not try to absorb the whole post in one pass. For each diagram,
write one sentence in this form:

```text
Input starts as ___, becomes ___, then ___ happens, producing ___.
```

If you cannot fill one blank, pause and map that blank back to one of these concepts:

- token
- embedding
- vector
- context
- attention
- transformer block
- training
- inference

That missing blank is the next thing to revise.

## Exit Test

Before starting the blog, answer these without looking:

1. What is a token?
2. Why does the model convert tokens into embeddings?
3. Why are vectors useful for neural networks?
4. What does context mean in an LLM?
5. What problem does attention solve?
6. What are query, key, and value in plain language?
7. Why did transformers become more useful than RNNs for LLMs?
8. What changes during training?
9. What happens during inference?
10. Why does an LLM generate text one token at a time?

If you can answer most of these simply, you are ready to start Jay Alammar again.

Answer key:

1. A token is a chunk of text represented by an ID. It might be a word, part of a word, punctuation,
   a space, or another text fragment.
2. The model converts tokens into embeddings because token IDs are just labels. Embeddings turn
   those labels into learned vectors that carry useful information for the neural network.
3. Vectors are useful because neural networks operate on numbers, and vectors can encode many fuzzy
   features of language at once.
4. Context is the sequence of tokens the model can currently use when predicting the next token.
5. Attention solves the problem of deciding which other tokens are relevant to the current token.
6. Query is what a token is looking for, key is what each token offers for matching, and value is the
   information that gets passed along.
7. Transformers became more useful than RNNs because attention lets tokens connect across a sequence
   more directly, and the architecture trains much more efficiently in parallel.
8. During training, the model's weights change. The model practices next-token prediction and uses
   errors to adjust its parameters.
9. During inference, the model's weights are used to produce output. The prompt goes in, the model
   predicts a next token, adds it to the context, and repeats.
10. An LLM generates text one token at a time because it is trained as a next-token predictor. Each
    new token becomes part of the input for predicting the following token.

## Next: 2.3 RAG Path

If the RAG material feels like too much text, switch to video first. RAG is easier once the loop is
visible:

```text
user question -> retrieve relevant chunks -> add chunks to prompt -> LLM answers
```

Recommended order:

1. Start with DeepLearning.AI's
   [Retrieval Augmented Generation (RAG)](https://www.deeplearning.ai/alpha/courses/retrieval-augmented-generation-rag)
   course. Focus only on Module 1 first: RAG overview, architecture, LLM calls, and information
   retrieval.
2. After that, return to the text/blog. The blog should make more sense once the retrieval
   loop is already familiar.
3. If the blog still feels abstract, use a small practical build to anchor the concepts.

RAG todo:

- [ ] Read the 2.3 RAG blog/material now that the basic loop is familiar.
- [ ] Work through [langchain-ai/rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch)
  as the hands-on follow-up.
- [ ] Save
  [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag)
  for later, after basic RAG feels comfortable.

Tiny note to write before starting the blog:

```text
RAG-MENTAL-MODEL.md

- retrieval
- chunking
- embeddings
- vector search
- prompt augmentation
- generation
```
