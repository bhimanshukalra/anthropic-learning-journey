LLM - Large Language Model

Neural Network - predicts the next word in the sequence

Think of LLMs as mostly inscrutable artifacts.

## How to train your ChatGPT

Stage 1: Pretraining

1. Download ~10TB of text.
2. Get a cluster of ~6,000 GPUs.
3. Compress the text into a neural network, pay ~2M, wait ~12 days.
4. Obtain base model.

Stage 2: Finetuning

1. Write labelling instructions.
2. Hire people, collect 100K high quality ideal Q&A responses, and/or comparisions.
3. Finetune base model on this data, wait ~1 day.
4. Obtain assistant model.
5. Run a lot of evaluations.
6. Deploy
7. Monitor, collect misbehaviours, go to step 1.

## Comparisons

It is often easier to compare answers instead of writing answers.

## RLHF

Reinforcement Learning From Human Feedback

## Bigger model

If we train a bigger model for more time, the model is better

## Self improvement

## LLM OS

## Security

## Types of models

Encoder-only models: Good for tasks that require understanding of the input, such as sentence classification and named entity recognition.
Decoder-only models: Good for generative tasks such as text generation.
Encoder-decoder models or sequence-to-sequence models: Good for generative tasks that require an input, such as translation or summarization.

## Attention layers

this layer will tell the model to pay specific attention to certain words in the sentence you passed it (and more or less ignore the others) when dealing with the representation of each word.

## How language models work

Language models work by being trained to predict the probability of a word given the context of surrounding words. This gives them a foundational understanding of language that can generalize to other tasks.

There are two main approaches for training a transformer model:

Masked language modeling (MLM): Used by encoder models like BERT, this approach randomly masks some tokens in the input and trains the model to predict the original tokens based on the surrounding context. This allows the model to learn bidirectional context (looking at words both before and after the masked word).

Causal language modeling (CLM): Used by decoder models like GPT, this approach predicts the next token based on all previous tokens in the sequence. The model can only use context from the left (previous tokens) to predict the next token.

## Types of language models

In the Transformers library, language models generally fall into three architectural categories:

- Encoder-only models (like BERT): These models use a bidirectional approach to understand context from both directions. They’re best suited for tasks that require deep understanding of text, such as classification, named entity recognition, and question answering.

The pretraining of these models usually revolves around somehow corrupting a given sentence (for instance, by masking random words in it) and tasking the model with finding or reconstructing the initial sentence.

- Decoder-only models (like GPT, Llama): These models process text from left to right and are particularly good at text generation tasks. They can complete sentences, write essays, or even generate code based on a prompt.

The pretraining of decoder models usually revolves around predicting the next word in the sentence.

- Encoder-decoder models (like T5, BART): These models combine both approaches, using an encoder to understand the input and a decoder to generate output. They excel at sequence-to-sequence tasks like translation, summarization, and question answering.

---

Most modern Large Language Models (LLMs) use the decoder-only architecture.
