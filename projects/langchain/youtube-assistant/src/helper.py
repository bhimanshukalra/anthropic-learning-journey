from dotenv import load_dotenv
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

VIDEO_QUERY_PROMPT = """
You are a helpful assistant that that can answer questions about youtube videos 
based on the video's transcript.

Answer the following question: {question}
By searching the following video transcript: {docs}

Only use the factual information from the transcript to answer the question.

If you feel like you don't have enough information to answer the question, say "I don't know".

Your answers should be verbose and detailed.
"""


def create_vector_db_from_youtube_url(video_url: str):
    try:
        loader = YoutubeLoader.from_youtube_url(video_url)
        transcript = loader.load()

        text_splitter = RecursiveCharacterTextSplitter()
        docs = text_splitter.split_documents(transcript)

        db = FAISS.from_documents(docs, embeddings)
        return db
    except Exception as e:
        print(f"Error: {str(e)}")


def get_response_from_query(db: FAISS, query: str, k: int = 4):
    docs = db.similarity_search(query, k)
    docs_page_content = " ".join([doc.page_content for doc in docs])

    model = ChatGoogleGenerativeAI(model="gemini-3.6-flash", thinking_level="medium")

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=VIDEO_QUERY_PROMPT,
    )

    chain = prompt | model | StrOutputParser()

    response = chain.invoke({"question": query, "docs": docs_page_content})
    return response
