LLM predicts next token and not word. 1 token is around 4 characters or 3/4 of a word.

## Classification

LLM can categorise customer query into primary and second categories. Based on the catogory we can come op with the next step

## Moderation

Use openai's moderation API to check if request is safe to process. Primary cateogries include hate, threat, self-harm, sexual, violence etc.

## Prompt injection

When dealing with user input use delimiters and clear instructions. Additionally, use a second prompt to ask if the user is doing prompt injection.
