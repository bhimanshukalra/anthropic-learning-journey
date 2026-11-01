# Retrieval Augmented Generation (RAG)

- Using a vector database as an external knowledge base
- Retrieve relevant info and provide to LLM
- Synergises with a vector db

## Advantages

- Reduce hallucinations
- Enables an LLM to cite sources
- Solve knowledge intensive tasks

## Langchain

### Document loading

Langchain provides a variety of loaders through which we can access different types of structured and unstructured data.
Examples: PyPDFLoader, YoutubeAudioLoader, WebBaseLoader, NotionDirectoryLoader etc.

Fetch youtube video locally:

url="https://www.youtube.com/watch?v=jGwO_UgTS7I"
save_dir="docs/youtube/"
loader = GenericLoader(
#YoutubeAudioLoader([url],save_dir), # fetch from youtube
FileSystemBlobLoader(save_dir, glob="\*.m4a"), #fetch locally
OpenAIWhisperParser()
)
docs = loader.load()

### Document splitting

Example:

1. r_splitter = RecursiveCharacterTextSplitter(
   chunk_size=150,
   chunk_overlap=0,
   separators=["\n\n", "\n", "(?<=\. )", " ", ""]
   )
   r_splitter.split_text(some_text)

   Text is recursively being split based on the characters passed in `separator`. First, it's being split on the first separator. If it's still bigger than the chunk size, then second, third, and so on and so forth.

2. TokenTextSplitter
3. NotionDirectoryLoader

### Retrieval

Maximum marginal relevance (MMR) is a search and retrieval technique that balances query relevance with result diversity to eliminate redundancy.

Examples:

1. Simple search: smalldb.similarity_search(question, k=2)

   using mmr: smalldb.max_marginal_relevance_search(question,k=2, fetch_k=3)

2. docs = vectordb.similarity_search(
   question,
   k=3,
   filter={"source":"docs/cs229_lectures/MachineLearning-Lecture03.pdf"}
   )

### Self-query retriever

from langchain.llms import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

metadata_field_info = [
AttributeInfo(
name="source",
description="The lecture the chunk is from, should be one of `docs/cs229_lectures/MachineLearning-Lecture01.pdf`, `docs/cs229_lectures/MachineLearning-Lecture02.pdf`, or `docs/cs229_lectures/MachineLearning-Lecture03.pdf`",
type="string",
),
AttributeInfo(
name="page",
description="The page from the lecture",
type="integer",
),
]

document_content_description = "Lecture notes"
llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0)
retriever = SelfQueryRetriever.from_llm(
llm,
vectordb,
document_content_description,
metadata_field_info,
verbose=True
)

question = "what did they say about regression in the third lecture?"

docs = retriever.get_relevant_documents(question)

### Using ContextualCompression with mmr

compression_retriever = ContextualCompressionRetriever(
base_compressor=compressor,
base_retriever=vectordb.as_retriever(search_type = "mmr")
)

question = "what did they say about matlab?"
compressed_docs = compression_retriever.get_relevant_documents(question)
pretty_print_docs(compressed_docs)

### Question-Answering

from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(
llm,
retriever=vectordb.as_retriever()
)

### Prompt

from langchain.prompts import PromptTemplate

template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

qa_chain = RetrievalQA.from_chain_type(
llm,
retriever=vectordb.as_retriever(),
return_source_documents=True,
chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

### Chain types

: map_reduce, refine, map_rerank

1. map_reduce: Independent LLM call to generate partial output, all are collected and combined into a final prompt
2. refine: For every subsequent LLM call, both the new chunk and the previous running response are passed.
3. map_rerank: for each chunk, along with answer a relevance/confidence score is received. Outputs the single answer that received the highest score

Example:

qa_chain_mr = RetrievalQA.from_chain_type(
llm,
retriever=vectordb.as_retriever(),
chain_type="map_reduce"
)
result = qa_chain_mr({"query": question})
result["result"]
