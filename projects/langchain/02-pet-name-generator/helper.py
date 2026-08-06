from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
