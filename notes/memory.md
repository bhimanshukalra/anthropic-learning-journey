Memory types

1. ConversationBufferMemory: this memory allows for storing of messages and then extracts the messages in a variable.

2. ConversationBufferWindowMemory: this memory keeps a list of the interactions of the conversation over time. It only uses the last K interactions.

3. ConversationTokenBufferMemory: this memory keeps a buffer of recent interactions in memory, and uses token length rather than number of interactions to determine when to flush interaction

4. ConversationSummaryMemory: this memory creates a summary of the conversation over time.

5. Vector data memory: stores text (from a conversation or elsewhere in a vector database and retrieves the most relevant blocks of text.)

6. Entity memories: using an LLM, it remembers details about specific entities

You can also use multiple memories at one time. e.g., conversation memory + entity memory to recall individuals.
