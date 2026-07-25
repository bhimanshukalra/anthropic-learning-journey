# AI Foundations

**Goal:** Define every AI topic from the absolute basics — skipping nothing — so this file becomes a strong foundation that can be referenced time and again. Quick, to-the-point definitions, ordered from basics upward.

## Recommended Resources

- **3Blue1Brown — Neural Networks series (YouTube):** ch. 1–4 = neurons, gradient descent, backprop (Batches 1/1a/1b); ch. 5–8 = LLMs, transformers, attention, embeddings (Batch 3). Best visual intuition; watch first.
- **Andrej Karpathy — "Deep Dive into LLMs like ChatGPT" (YouTube, ~3.5h):** tokenization → next-token prediction → sampling → pre-training → fine-tuning → RLHF → hallucinations (Batches 1c/2/4). Shorter option: his 1h "Intro to Large Language Models."
- **Jay Alammar — "The Illustrated Transformer" (blog):** second pass on attention/transformer in a different visual language.
- **Anthropic Academy (anthropic.com/learn):** Claude API, prompting, tool use, RAG, agents (Batch 5) — uses the exam's own vocabulary.
- Skip for now: Karpathy's "Zero to Hero" (code-it-from-scratch — ML-engineer depth, beyond our line).

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

### Vocabulary

The model's fixed menu of ~100k tokens — a keyboard with 100,000 keys (whole common words, word-pieces, characters, punctuation), each with a permanent ID. All input is decomposed into these keys; all output is assembled from them; nothing else can ever be said. Built before training by picking the chunks that most efficiently cover text, then frozen forever — the model can learn new concepts from context but never grow a new key. It's why the probability table has a fixed size (one score per entry), and why models fumble letter-counting ("r's in strawberry") — they see token IDs, not letters.

### Embedding

Each vocabulary token's learned "meaning profile" — a list of a few thousand numbers (sliders) encoding how that token behaves: grammar, topic, tone, company it keeps. Learned as parameters during training, which naturally pushes related tokens toward similar profiles (" Paris" ≈ " Rome" on most sliders). Embeddings are what turn meaningless token IDs into numbers that carry meaning.

### Attention

The mechanism that customizes each token's generic scorecard to this sentence. Every token broadcasts a question ("query": what am I looking for?), an advert ("key": what do I offer?), and a payload ("value": the info I'll share) — all computed from its scorecard by learned weights. Each token's question is similarity-matched against every other token's advert; each token then absorbs a match-weighted blend of the payloads. Result: "it" becomes "it-meaning-that-cat"; "bank" becomes river-bank. One line: every token looks at every other token, scores relevance, and absorbs a weighted blend of their information.

### Multi-Head Attention

Each attention step runs dozens of parallel attention operations ("heads"), each with its own learned question/advert/payload weights, free to specialize in different relationships — pronoun reference, previous-word, syntax, topic. Specialties aren't assigned; they emerge from training (like embedding traits): humans design the container, gradient descent fills in the structure.

### Positional Encoding

Attention compares scorecards with no built-in sense of word order — unpatched, "dog bites man" = "man bites dog." Fix: stamp each token's position (1st, 2nd, 3rd...) onto its scorecard before attention, so questions can be order-aware ("noun before me").

### Transformer

The architecture of all modern LLMs. One block = attention (tokens talk to each other, gathering context) + feed-forward network (each token thinks alone, digesting what it gathered) — talk, then think. Stack the block dozens-to-100+ deep: early blocks resolve grammar/references, deeper blocks compose meaning and facts; the final position's scorecard becomes the prediction profile that scores the vocabulary. Why it won (2017, "Attention Is All You Need"): RNNs read one token at a time and long-range context faded; transformers process all tokens in parallel (GPU-friendly) and any token reaches any other in one hop — scalable to internet-size data, making the "large" in LLM possible.

### How the Probability Table Is Built (Forward Pass)

Four steps. (1) Embed: each prompt token swaps its ID for its meaning profile. (2) Contextualize: layer by layer, every token's profile blends in information from neighboring tokens (attention) — "capital" shifts toward city-capital because "France" is nearby; by the last layer, the final position holds a "prediction profile": the shape of what should come next. (3) Score: the prediction profile is compared for similarity (dot product) against every vocabulary token's output profile — ~100k similarity scores at once, the logits. No lookup or search; pure learned geometry. (4) Softmax: raise e to each score (amplifies gaps, e.g. 9 vs 6 → 20×) then divide by the total → percentages summing to 100% (" Paris" 95%, " London" 4.7%). Temperature plugs in just before the amplify step.

### Softmax

The scores→percentages converter at the end of the forward pass: exponentiate every raw score (all positive, gaps amplified), then divide each by the sum so everything totals 100%. Turns ~100k logits into the probability table that sampling draws from.

### Next-Token Prediction (How Generation Works)

The single thing an LLM does. One forward pass: prompt tokens flow through the layers → final layer outputs a raw score per vocabulary token (~100k numbers, called logits) → softmax converts scores into probabilities summing to 100% (e.g., " Paris" 92%). Then pick one: greedy (always take the top — deterministic but repetitive) or sampling (weighted dice roll — the source of non-determinism; temperature reshapes the table before the roll). Append the chosen token, re-run the whole sequence for the next table, loop until a stop token or max-token limit — this loop is autoregressive generation. Consequences: streaming is literal (tokens are made one at a time), output tokens dominate latency (one full forward pass each), and hallucination isn't lying — the model always just samples its table, and there is no truth-checking step in the loop.

### Hallucination

The model stating false information fluently and confidently (fabricated citations, plausible-but-wrong facts). Not a malfunction — the generation loop working as designed: the probability table is shaped by training-data patterns, not a lookup of verified facts, and there is no truth-checking step anywhere in the loop. Where data was dense, confidence tracks truth; where it was thin or contradictory, the most plausible continuation may be false — "sounding right" and "being right" come from the same mechanism, so they fail together. Traps: temperature 0 does NOT fix it (a confidently wrong table just hallucinates deterministically), and bigger models reduce but never eliminate it. Real mitigations ground the answer outside the weights: RAG, tool use, citation requirements.

### LLM (Large Language Model)

A model — specifically a very large neural network — whose parameters were set using the ML training recipe (gradient descent on a loss), where the training task was next-token prediction over massive amounts of text. Every level of the stack applies: it's AI (performs intelligence-like tasks), ML (behavior learned from data, not hand-coded), deep learning (the model is a many-layered neural network), and a model (one big function: token numbers in → probability scores out). "Large" = billions of parameters; "Language" = the training data. Precise phrasing: an ML model trained by gradient descent — ML names the field, gradient descent + backpropagation is the mechanism.

## Generation Controls (Inference-Time Settings)

One picture: context window bounds what goes in; temperature and top-p shape how the dice are rolled; max tokens bounds what comes out.

### Context Window

The model's working memory: the max tokens considerable in one forward pass (Claude: 200k). Everything must fit — system prompt, documents, conversation history, and the answer generated so far. The model is stateless: chat apps resend the whole conversation every turn; anything outside the window does not exist for the model. Explains why long chats forget their start, why "paste everything" has a ceiling, and why RAG exists (fetch only the relevant slice in). Wrinkle: info at the start/end of a long context is handled better than the middle ("lost in the middle").

### Temperature

Reshapes the probability table before the dice roll (plugs in before softmax's amplify step): low → gaps exaggerated, leader dominates (T=0 = greedy, near-deterministic); 1 → table as trained; high → table flattens, underdogs win often, eventually incoherent. The dial: "how much should the leader dominate?" Low (0–0.3) for extraction/code/factual; higher (0.7–1) for creative work. Trap: T=0 buys consistency, not correctness — a confidently wrong table hallucinates identically every run.

### Top-p (Nucleus Sampling)

Truncates the table instead of reshaping it: keep the smallest top set of tokens summing to p (e.g. 90%), discard the entire tail, re-scale survivors, roll only among them. Adaptive: confident table → 1–2 survivors (effectively greedy); uncertain table → many survivors (creative freedom preserved). Kills the 99k-token tail so fluke rolls can't pick gibberish. Sibling top-k keeps a fixed count instead (cruder). Rule: tune temperature OR top-p, not both.

### Max Tokens

Hard cap on output length: generation stops at the model's stop token or this cap, whichever first — cap = truncation mid-sentence (check the API's stop/finish reason; handle truncation in code). Not a target (the model doesn't know it exists — control length via the prompt) and not quality control — a cost/latency guardrail, since output tokens are the slow, expensive ones.

## How Claude-Like Models Are Made

### Pre-Training

The giant first training stage where the model learns language, facts, patterns, reasoning shapes, code, style, and world structure from massive text/data. The training task is still simple: predict the next token. Given "The capital of France is", the model learns to assign high probability to "Paris".

Pre-training is not just memorizing facts. By doing next-token prediction across enormous data, the model learns grammar, syntax, programming conventions, math forms, question-answer patterns, and relationships between concepts. It gives the model raw capability, but not necessarily assistant behavior. A pre-trained-only model may continue text in a plausible style without reliably following instructions.

One line: pre-training teaches the model how language/world patterns work.

### Fine-Tuning

Additional training after pre-training, usually on a smaller curated dataset. The model already knows language; fine-tuning nudges it toward a desired behavior.

For assistant models, an important kind is instruction fine-tuning: examples shaped like "User asks for X; assistant gives the desired response." This teaches the model to answer the user, follow instructions, use an assistant tone, produce requested formats, refuse certain unsafe requests, and prefer helpful completions over random continuations.

Fine-tuning usually should not be the first choice for adding private knowledge. If the model needs a company handbook, RAG is usually better. Fine-tuning is better for behavior, style, format, repeated task pattern, or latency/cost trade-offs.

One line: fine-tuning teaches the model how you want it to behave.

### RLHF (Reinforcement Learning from Human Feedback)

A preference-training method that teaches a model which responses humans tend to prefer. Rough flow: the model produces multiple answers to the same prompt; humans rank them; a reward model learns those preferences; the assistant model is further trained to produce answers that score well under that reward model.

RLHF helps make models more helpful, harmless, honest-ish, conversational, and aligned with human preferences. But it has trade-offs: it can make models overly agreeable, verbose, refusal-prone, or optimized for "sounds good to humans" rather than "is objectively correct." This is why evals, grounding, and external verification still matter.

One line: RLHF teaches the model which behaviors humans prefer.

### Pre-Training vs Fine-Tuning vs RLHF

Think of making a professional engineer. Pre-training is years of reading the internet, books, code, documentation, and examples. Fine-tuning is job-specific examples: "when a user asks this, respond like this." RLHF is managers/users comparing outputs and saying which answer is better.

| Stage | Teaches | Dataset size | Main effect |
|---|---|---:|---|
| Pre-training | Language/world/code patterns | Huge | Raw capability |
| Fine-tuning | Desired task/assistant behavior | Smaller | Instruction-following |
| RLHF | Human preference | Smaller but curated | Helpfulness/alignment |

### System Prompt

A high-priority instruction given to the model before the user message. It can define role, tone, boundaries, output format, safety constraints, tool-use rules, and domain-specific behavior. Example: "You are a concise technical tutor. Explain concepts with examples. Do not skip prerequisites."

A system prompt does not change the model's weights. It is runtime steering, not learning. Fine-tuning changes the model; system prompting steers the model during a request.

One line: a system prompt is inference-time steering, not training.

### Instruction-Following

The model's learned ability to treat user text as a task to perform, not just text to continue. A raw language model may see "Translate this to French: good morning" as text to continue. An instruction-following assistant understands the task and replies "Bonjour."

This behavior comes from instruction fine-tuning and preference training. It includes obeying constraints like "answer in JSON," "use exactly three bullets," "ask one clarifying question first," or "do not mention implementation details."

Instruction-following is imperfect. Models can ignore constraints, over-follow irrelevant instructions, or get confused when documents contain malicious instructions. AI engineering compensates with structured outputs, validation, evals, tool permissions, and prompt-injection defenses.

### Training-Time vs Inference-Time

A Claude-like assistant is roughly: base model from pre-training + instruction fine-tuning + preference/alignment training + system prompt at runtime + user/developer messages + tools/RAG/context = assistant behavior.

Training-time things change or shape the weights: pre-training, fine-tuning, RLHF, and related alignment methods. Inference-time things steer a frozen model during use: system prompts, user prompts, API parameters, tools, RAG documents, and context-window management.

As an AI engineer, you mostly work at inference time. You usually do not train Claude. You build systems around it: prompts, APIs, tools, retrieval, evals, monitoring, and product workflows.

## Building on Top of LLMs

### Prompt

The natural-language/task instruction you send to the model at inference time. A prompt can include the user's request, background context, examples, constraints, output format, and any documents the model should use.

A prompt does not change the model's weights. It is steering for this one request or conversation. Good prompting is not magic wording; it is clear task design: tell the model what role it is playing, what information matters, what output shape is required, what constraints apply, and what to do when the answer is unknown.

One line: a prompt is the task/context you give a frozen model so it can produce the desired next tokens.

### Prompt vs API Parameters

Prompts control meaning and task behavior; API parameters control generation mechanics and request limits. They work together, but they are different kinds of control.

Prompt examples: "answer in JSON," "cite sources," "be concise," "use only the provided document," "ask a clarifying question first." These instructions shape what the model tries to do.

API parameter examples: `temperature`, `top_p`, `max_tokens`, `stop_sequences`, model name, streaming on/off, tool definitions, and sometimes response-format/schema options. These settings shape how the model generates or how the API wraps the generation.

If the answer is too creative, adjust temperature/top-p. If the answer is the wrong format, improve the prompt and add structured-output validation. If the answer is cut off, increase `max_tokens` or ask for a shorter answer. If the answer invents facts, add grounding via RAG/tool use and evals; temperature alone does not solve truth.

One line: prompts say what to do; API parameters say how generation should be sampled, bounded, structured, or connected to tools.

### Context

The information included in the request that the model can directly attend to: system prompt, user message, conversation history, documents, tool results, retrieved chunks, images, and the answer generated so far. The model only knows what is in its weights plus what is present in the current context window.

Context is not memory in the human sense. If a fact is not in the model's weights and not in the current context, the model cannot reliably use it. Chat apps create the illusion of memory by resending prior turns; RAG creates task-specific context by fetching relevant external information.

One line: context is the model's temporary working material for the current request.

### Grounding

Giving the model external evidence to base its answer on, instead of relying only on patterns stored in weights. Grounding can come from retrieved documents, database queries, API calls, search results, tool outputs, or user-provided files.

Grounding reduces hallucination risk because the answer can be tied to specific evidence, but it does not guarantee correctness. The system can retrieve the wrong evidence, omit the right evidence, misread the evidence, or cite sources that do not actually support the answer. This is why grounded systems need evals that separate retrieval quality from answer quality.

One line: grounding means forcing the model's answer to lean on external evidence.

### RAG (Retrieval-Augmented Generation)

A pattern where the system retrieves relevant information from an external corpus and places it into the model's context before asking the model to answer. It is "retrieval-augmented" because the model's generation is augmented by fetched evidence.

Basic flow: user asks a question → system searches documents → top relevant chunks are inserted into the prompt/context → model answers using those chunks → system returns answer, often with citations.

RAG is useful when the model needs fresh, private, large, or source-specific knowledge: company docs, product manuals, tickets, policies, research papers, PDFs, or databases. It is usually better than fine-tuning for knowledge injection because the source material can be updated without retraining and the answer can cite evidence.

RAG has two different failure modes. Retrieval failure: the right evidence was not fetched. Generation failure: the right evidence was fetched but the model answered incorrectly, ignored it, or failed to cite it. A good AI engineer diagnoses these separately.

One line: RAG fetches relevant external knowledge and gives it to the model at inference time.

### Embeddings for Retrieval

An embedding for retrieval is a vector representation of a text/document chunk/query, where semantic similarity becomes geometric closeness. If a user asks "refund window," a good embedding search may retrieve a policy chunk saying "returns accepted within 30 days," even though the exact words differ.

In RAG, documents are split into chunks, each chunk is embedded, and those vectors are stored in a vector database. At query time, the user question is embedded too; the system finds nearby vectors and returns the matching chunks.

Embeddings are powerful for semantic search, but they are not enough by themselves. Keyword search can outperform embeddings for exact names, IDs, error codes, and rare terms. This is why production RAG often uses hybrid search: vector similarity plus keyword/BM25.

One line: embeddings turn text into searchable geometry.

### Chunking

Splitting documents into smaller pieces before indexing them for retrieval. Chunks must be small enough to search and fit into context, but large enough to preserve meaning.

Naive chunking can destroy meaning. A chunk may separate a heading from its paragraph, a table from its explanation, or a policy condition from its exception. Better chunking respects structure: sections, headings, pages, tables, paragraphs, and source metadata.

Chunking is a design trade-off. Smaller chunks can retrieve precise snippets but may lack context. Larger chunks preserve context but may retrieve irrelevant material and waste tokens. The right answer is empirical: test chunk sizes against retrieval and answer evals.

One line: chunking decides what unit of knowledge the retrieval system can find.

### Citation

A pointer from the model's answer back to the source evidence it used: document, page, section, URL, row, or chunk. Citations make answers inspectable and help users decide whether to trust them.

A citation is only useful if it actually supports the claim. "Has a citation" is weaker than "the citation proves the sentence." Good RAG evals check citation accuracy, not just citation presence.

One line: citations make generated answers traceable to evidence.

### Tool Use / Function Calling

A pattern where the model can request that the application call a predefined tool/function, then use the result in its next response. The model does not directly execute arbitrary code; it emits a structured tool call, and your application decides whether and how to run it.

Example: the user asks "What's the weather in Delhi tomorrow?" The model decides it needs a weather tool and returns a call like `get_weather(location="Delhi", date="tomorrow")`. Your code validates the arguments, calls the weather API, sends the result back to the model, and the model writes the final answer.

Tools are useful when the model needs fresh data, private data, calculations, actions, or side effects: search, database lookup, ticket creation, calendar scheduling, file operations, payments, or code execution. They turn the model from a text generator into a reasoning-and-routing layer around real software capabilities.

Tool use must be bounded. The application should define allowed tools, validate arguments, enforce permissions, handle errors/timeouts, log calls, and require human approval for consequential actions.

One line: tool use lets the model ask your software to do specific, controlled things.

### Tool Schema

The machine-readable contract that tells the model what a tool does, what arguments it accepts, which fields are required, and what types/constraints apply. It is usually expressed as JSON Schema or a similar structured definition.

Good tool schemas are narrow and explicit. A tool named `refund_order(order_id, reason)` is safer than a vague tool named `run_admin_action(action)`. The model is better at choosing and filling tools when names, descriptions, and parameters are concrete.

One line: a tool schema is the API contract between the model and your application.

### Tool-Call Loop

The control loop around tool use. Typical flow: user asks → model responds with a tool call → application validates and executes the tool → application sends the tool result back to the model → model either answers or requests another tool → loop stops at a final answer, error, escalation, or budget limit.

The loop belongs to your application, not the model. Your code owns stopping conditions, retries, permissions, idempotency, traces, and error handling. This is where many agent systems succeed or fail.

One line: the tool-call loop is the application harness that turns model tool requests into controlled execution.

### Function Calling vs Tool Use

Function calling is the older/common term for the same basic idea: the model emits a structured request to call a function. Tool use is the broader term: tools may be functions, APIs, database queries, MCP tools, file actions, browser actions, or other controlled capabilities.

The model is not "calling" the function by itself. It is selecting a tool and proposing arguments; the host application performs the actual call.

One line: function calling is structured tool selection; tool use is the broader product pattern.

### Prompting vs RAG vs Tool Use

These are three different ways to improve a model-backed product.

Prompting is best when the model already has enough knowledge/capability and needs clearer instructions, examples, constraints, or output format.

RAG is best when the model needs external knowledge: private docs, changing facts, large corpora, policies, PDFs, or answers that need citations.

Tool use is best when the model needs to take an action, fetch live structured data, calculate reliably, query a system of record, or interact with software.

One line: prompt for behavior, RAG for knowledge, tools for actions/live systems.

### Building on Top vs Training the Model

Most AI engineering work happens around a frozen model. You design prompts, schemas, retrieval, tools, evals, logging, permissions, and product flows. You are not usually changing the model's weights.

This is why app-layer AI engineering looks like software engineering plus probabilistic-system discipline: APIs, data modeling, tests, evals, observability, UX, security, cost, and latency.

One line: building on top means turning a general model into a reliable product through surrounding software.

## Agentic Patterns

### Evaluator-Optimizer Pattern

An agentic workflow where one LLM (optimizer) generates a response and a second LLM (evaluator) critiques it against defined criteria, looping feedback back for revision until the criteria are met.
