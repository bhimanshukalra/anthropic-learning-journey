## OpenAI Function Calling

import json

// Example dummy function hard coded to return the same weather

// In production, this could be your backend API or an external API

def get_current_weather(location, unit="fahrenheit"):
"""Get the current weather in a given location"""
weather_info = {
"location": location,
"temperature": "72",
"unit": unit,
"forecast": ["sunny", "windy"],
}
return json.dumps(weather_info)

// define a function

functions = [
{
"name": "get_current_weather",
"description": "Get the current weather in a given location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g. San Francisco, CA",
},
"unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
},
"required": ["location"],
},
}
]

messages = [
{
"role": "user",
"content": "What's the weather like in Boston?"
}
]

// Call the ChatCompletion endpoint
response = openai.ChatCompletion.create( # OpenAI Updates: As of June 2024, we are now using the GPT-3.5-Turbo model
model="gpt-3.5-turbo",
messages=messages,
functions=functions,
function_call="auto",
)

## function_call

1. auto - default (LLM decides if a function should be called or not)
2. none - function should be called
3. function_call={"name": "get_current_weather"} - function name is explicitely passed and a function call will be returned in the response

# LCEL

Why LCEL:

1. Async, batch and streaming support
2. Fallbacks
3. Parallelism
4. Logging is built in

## Simple chain

prompt = ChatPromptTemplate.from_template(
"tell me a short joke about {topic}"
)
model = ChatOpenAI()
output_parser = StrOutputParser()

chain = prompt | model | output_parser

chain.invoke({"topic": "bears"})

## Complex chain

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayInMemorySearch

vectorstore = DocArrayInMemorySearch.from_texts(
["harrison worked at kensho", "bears like to eat honey"],
embedding=OpenAIEmbeddings()
)

retriever = vectorstore.as_retriever()

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

from langchain.schema.runnable import RunnableMap

chain = RunnableMap({
"context": lambda x: retriever.get_relevant_documents(x["question"]),
"question": lambda x: x["question"]
}) | prompt | model | output_parser

chain.invoke({"question": "where did harrison work?"})

## Bind

functions = [
{
"name": "weather_search",
"description": "Search for weather given an airport code",
"parameters": {
"type": "object",
"properties": {
"airport_code": {
"type": "string",
"description": "The airport code to get the weather for"
},
},
"required": ["airport_code"]
}
}
]

prompt = ChatPromptTemplate.from_messages(
[
("human", "{input}")
]
)
model = ChatOpenAI(temperature=0).bind(functions=functions)

runnable = prompt | model

runnable.invoke({"input": "what is the weather in sf"})

functions = [
{
"name": "weather_search",
"description": "Search for weather given an airport code",
"parameters": {
"type": "object",
"properties": {
"airport_code": {
"type": "string",
"description": "The airport code to get the weather for"
},
},
"required": ["airport_code"]
}
},
{
"name": "sports_search",
"description": "Search for news of recent sport events",
"parameters": {
"type": "object",
"properties": {
"team_name": {
"type": "string",
"description": "The sports team to search for"
},
},
"required": ["team_name"]
}
}
]

model = model.bind(functions=functions)

runnable = prompt | model

runnable.invoke({"input": "how did the patriots do yesterday?"})

// simple_chain is executed, if there's an error then chain will be executed
final_chain = simple_chain.with_fallbacks([chain])

## Pydantic

class pUser(BaseModel):
name: str
age: int
email: str

---

model_with_function = model.bind(functions=[weather_function])
model_with_function.invoke("what is the weather in sf?")

---

class WeatherSearch(BaseModel):
"""Call this with an airport code to get the weather at that airport"""
airport_code: str = Field(description="airport code to get weather for")

class ArtistSearch(BaseModel):
"""Call this to get the names of songs by a particular artist"""
artist_name: str = Field(description="name of artist to look up")
n: int = Field(description="number of results")

functions = [
convert_pydantic_to_openai_function(WeatherSearch),
convert_pydantic_to_openai_function(ArtistSearch),
]

model_with_functions = model.bind(functions=functions)
model_with_functions.invoke("what is the weather in sf?")
model_with_functions.invoke("what are three songs by taylor swift?")

## Tagging and Extraction

### Tagging

class Tagging(BaseModel):
"""Tag the piece of text with particular info."""
sentiment: str = Field(description="sentiment of text, should be `pos`, `neg`, or `neutral`")
language: str = Field(description="language of text (should be ISO 639-1 code)")

prompt = ChatPromptTemplate.from_messages([
("system", "Think carefully, and then tag the text as instructed"),
("user", "{input}")
])

model_with_functions = model.bind(
functions=tagging_functions,
function_call={"name": "Tagging"}
)

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

tagging_chain = prompt | model_with_functions | JsonOutputFunctionsParser()

tagging_chain.invoke({"input": "I love langchain"})

---

### Extraction

from typing import Optional
class Person(BaseModel):
"""Information about a person."""
name: str = Field(description="person's name")
age: Optional[int] = Field(description="person's age")

class Information(BaseModel):
"""Information to extract."""
people: List[Person] = Field(description="List of info about people")

extraction_functions = [convert_pydantic_to_openai_function(Information)]
extraction_model = model.bind(functions=extraction_functions, function_call={"name": "Information"})

prompt = ChatPromptTemplate.from_messages([
("system", "Extract the relevant information, if not explicitly provided do not guess. Extract partial info"),
("human", "{input}")
])

from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

extraction_chain = prompt | extraction_model | JsonKeyOutputFunctionsParser(key_name="people")

extraction_chain.invoke({"input": "Joe is 30, his mom is Martha"})

### Web page loader example

from langchain.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
documents = loader.load()

class Overview(BaseModel):
"""Overview of a section of text."""
summary: str = Field(description="Provide a concise summary of the content.")
language: str = Field(description="Provide the language that the content is written in.")
keywords: str = Field(description="Provide keywords related to the content.")

overview_tagging_function = [
convert_pydantic_to_openai_function(Overview)
]
tagging_model = model.bind(
functions=overview_tagging_function,
function_call={"name":"Overview"}
)
tagging_chain = prompt | tagging_model | JsonOutputFunctionsParser()

tagging_chain.invoke({"input": page_content})

class Paper(BaseModel):
"""Information about papers mentioned."""
title: str
author: Optional[str]

class Info(BaseModel):
"""Information to extract"""
papers: List[Paper]

paper_extraction_function = [
convert_pydantic_to_openai_function(Info)
]
extraction_model = model.bind(
functions=paper_extraction_function,
function_call={"name":"Info"}
)

extraction_chain = prompt | extraction_model | JsonKeyOutputFunctionsParser(key_name="papers")

### Routing

functions = [
format_tool_to_openai_function(f) for f in [
search_wikipedia, get_current_temperature
]
]
model = ChatOpenAI(temperature=0).bind(functions=functions)

from langchain.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
("system", "You are helpful but sassy assistant"),
("user", "{input}"),
])

from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.agent import AgentFinish
def route(result):
if isinstance(result, AgentFinish):
return result.return_values['output']
else:
tools = {
"search_wikipedia": search_wikipedia,
"get_current_temperature": get_current_temperature,
}
return tools[result.tool].run(result.tool_input)

chain = prompt | model | OpenAIFunctionsAgentOutputParser() | route

result = chain.invoke({"input": "What is the weather in san francisco right now?"})

### Conversational agent

1. Agents
   - are a combination of LLMs and code
   - LLMs reason about what steps to take and call for actions.
2. Agent loop
   - choose a tool to use
   - observe the output of the tool
   - repeat until a stopping condition is met
3. Stopping conditions can be:
   - LLM determined
   - Hardcoded rules

functions = [format_tool_to_openai_function(f) for f in tools]
model = ChatOpenAI(temperature=0).bind(functions=functions)

from langchain.prompts import MessagesPlaceholder
prompt = ChatPromptTemplate.from_messages([
("system", "You are helpful but sassy assistant"),
("user", "{input}"),
MessagesPlaceholder(variable_name="agent_scratchpad")
])

chain = prompt | model | OpenAIFunctionsAgentOutputParser()

from langchain.schema.runnable import RunnablePassthrough
agent_chain = RunnablePassthrough.assign(
agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
) | chain

from langchain.schema.agent import AgentFinish
def run_agent(user_input):
intermediate_steps = []
while True:
result = chain.invoke({
"input": user_input,
"intermediate_steps": intermediate_steps
})
if isinstance(result, AgentFinish):
return result
tool = {
"search_wikipedia": search_wikipedia,
"get_current_temperature": get_current_temperature,
}[result.tool]
observation = tool.run(result.tool_input)
intermediate_steps.append((result, observation))

from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True)

### Chat history

prompt = ChatPromptTemplate.from_messages([
("system", "You are helpful but sassy assistant"),
MessagesPlaceholder(variable_name="chat_history"),
("user", "{input}"),
MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent_chain = RunnablePassthrough.assign(
agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
) | prompt | model | OpenAIFunctionsAgentOutputParser()

from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history")
