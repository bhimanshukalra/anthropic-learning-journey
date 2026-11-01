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
