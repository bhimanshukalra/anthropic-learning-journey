from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_groq import ChatGroq
import wikipedia

load_dotenv()


def generate_pet_name(animal_type, animal_color):
    prompt_input_variables = ["animal_type", "animal_color"]
    prompt_template = "I have a pet {animal_type} and I want a cool name for it. It is {animal_color} in color. Suggest me five cool names for my pet."

    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash", thinking_level="medium", temperature=0.7
    )
    prompt = PromptTemplate(
        input_variables=prompt_input_variables,
        template=prompt_template,
    )

    chain = prompt | model | StrOutputParser()

    response = chain.invoke({"animal_type": animal_type, "animal_color": animal_color})
    return response


def generate_pet_name_agent(animal_type, animal_color):
    try:
        # model = ChatGoogleGenerativeAI(
        #     model="gemini-3.5-flash", thinking_level="medium", temperature=0.5
        # )
        model = ChatGroq(model="qwen/qwen3.6-27b", temperature=0.5)
        tools = [search_wikipedia, multiply]
        system_prompt = "You are a helpful assistant. Use tools when useful."

        agent = create_agent(model=model, tools=tools, system_prompt=system_prompt)

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"What is the average age of a {animal_color} {animal_type}? Multiply it by 3",
                    }
                ]
            }
        )

        last_message = response["messages"][-1]
        print("last content: ", last_message.content)
        return response
    except Exception as exc:
        print(f"Error generating pet name agent response: {exc}")
        return None


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a short summary for the best matching page."""
    try:
        return wikipedia.summary(query, sentences=3, auto_suggest=False)
    except Exception as exc:
        return f"Wikipedia search failed for {query!r}: {exc}"


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    generate_pet_name_agent("Dog", "Golden")
