## Types of LLms

1. Base LLM - predict next word, based on text training data.
2. Instruction tuned LLM - tries to follow instructions

   Fine tune on instructions and good attempts at following those instructions.

   RLHF: Reinforcement Learning with Human Feedback

   Helpful, Honest, Harmless

## Principle 1 - Write clear and specific instructions

Tactic 1: Use delimiters e.g. triple qoutes, angle brackets, xml tags, triple backticks, triple dashes

Tactic 2: Ask for structured output e.g. HTML, JSON

Tactic 3: Check whether conditions are satisfied - check assumptions required to do the task

Tactic 4: Few-shot prompting - give successful examples of completing tasks then ask model to perform the task

## Principle 2 - Give the model time to think

Tactic 1: Specify the steps to complete a task (breakdown a big task into smaller steps)

Tactic 2: Instruct the model to work out its own solution before rushing to a conclusion

## Model limitations

1. Hallucinations
2. Reducing hallucnations:

   a. first find relevant information

   b. then answer the question

   c. based on the relevant information.

## Iterative

### prompt development

1. Idea
2. Implementation (code/data) prompt
3. Experimental result
4. Error analysis

Step 1-4 create a loop

### Iterative process:

1. Try something.
2. Analyse where the result does not give what you want.
3. Clarify instructions, give more time to think.
4. Refine prmpts with a batch of examples.

## Summarisation

## Inferring

1. Sentiment analysis (positive/negative)
2. Identify all types of emotions in a given piece of text
3. Extract product & company name from customer reviews

## Transforming

1. Translation (LLMs can translate text and detect the language for a given piece of text)
2. Tone transformation (LLMs can identify and manipulate the tone of a given piece of text e.g. formal/informal.)
3. Format conversion (covert from JSON to markdown, HTML or a table)
4. Spell check/ grammer check

## Expanding (short text to large text)

Example: create an email based on the review provided by the customer.

## ChatBot

Pass messages array to LLM. Pass relevant system user and assistant roles.

## Pointers

- Be specific and set the scene

Define role, audience, tone and format

- Few shot prompting

Give 2-4 examples
Helpful for format, styles, edge cases, classification

- Chain of thought

reason step by step

- Structured output

Ask for response in JSON, tables, XML, or markdown

- Constraints & negative instructions

Example: length: "Summarise in exactly 3 bullet points", "Do not go beyond 100 words"

- Iterative refinement

- interview-style prompting: let the model ask

- System vs user prompts

System prompt: set idenity, rules, style etc.
User prompt: the actual request

- Prompt chaining
