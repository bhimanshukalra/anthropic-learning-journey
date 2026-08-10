from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator
from rich import print

load_dotenv()

llm = ChatGroq(model="qwen/qwen3.6-27b")


class EvaluationSchema(BaseModel):
    feedback: str = Field(description="Detailed feedback for the essay")
    score: int = Field(description="Score out of 10", ge=0, le=10)


structured_llm = llm.with_structured_output(EvaluationSchema)


class EssayState(TypedDict):

    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    individual_scores: Annotated[list[int], operator.add]
    avg_score: float


def evaluate_language(state: EssayState):
    prompt = f'Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {state["essay"]}'
    output = structured_llm.invoke(prompt)
    return {"language_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_analysis(state: EssayState):

    prompt = f'Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n {state["essay"]}'
    output = structured_llm.invoke(prompt)

    return {"analysis_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_thought(state: EssayState):

    prompt = f'Evaluate the clarity of thought of the following essay and provide a feedback and assign a score out of 10 \n {state["essay"]}'
    output = structured_llm.invoke(prompt)

    return {"clarity_feedback": output.feedback, "individual_scores": [output.score]}


def final_evaluation(state: EssayState):

    # summary feedback
    prompt = f'Based on the following feedbacks create a summarized feedback \n language feedback - {state["language_feedback"]} \n depth of analysis feedback - {state["analysis_feedback"]} \n clarity of thought feedback - {state["clarity_feedback"]}'
    overall_feedback = llm.invoke(prompt).content

    # avg calculate
    avg_score = sum(state["individual_scores"]) / len(state["individual_scores"])

    return {"overall_feedback": overall_feedback, "avg_score": avg_score}


graph = StateGraph(EssayState)

graph.add_node("evaluate_language", evaluate_language)
graph.add_node("evaluate_analysis", evaluate_analysis)
graph.add_node("evaluate_thought", evaluate_thought)
graph.add_node("final_evaluation", final_evaluation)

graph.add_edge(START, "evaluate_language")
graph.add_edge(START, "evaluate_analysis")
graph.add_edge(START, "evaluate_thought")

graph.add_edge("evaluate_language", "final_evaluation")
graph.add_edge("evaluate_analysis", "final_evaluation")
graph.add_edge("evaluate_thought", "final_evaluation")

graph.add_edge("final_evaluation", END)

workflow = graph.compile()

initial_state = {
    "essay": """The United States in the Age of AI: The Infrastructure and Capital Superpower

As the world navigates the maturing landscape of artificial intelligence in 2026, the United States stands as the undisputed epicenter of the AI revolution. Driven by an ecosystem of hyperscalers, massive venture capital, and a fiercely competitive free market, the US has transitioned AI from a phase of speculative experimentation into the fundamental backbone of its digital and physical economy. However, the American approach to AI is no longer just a story of software and algorithms; it has evolved into the most capital-intensive infrastructure buildout in modern history, testing the physical limits of the nation's energy grid and resources.

The defining characteristic of the US AI strategy is its sheer scale and rapid commercialization. Silicon Valley and major tech hubs have pioneered the shift toward "Agentic AI" and "Physical AI." Intelligence is no longer confined to chatbots on a screen; autonomous agents are now orchestrating complex, end-to-end enterprise workflows, while advanced robotics powered by massive neural networks are redefining logistics and manufacturing floors. For American corporations, the current era marks a structural reorganization where operating models are being fundamentally redesigned around human-machine collaboration rather than merely automating legacy processes.

Yet, this relentless pursuit of scale has collided with physical reality, triggering an unprecedented energy reckoning. The US is building massive AI data center clusters that require gigawatts of continuous power. With data center electricity consumption projected to more than double in a span of just a few years, the nation is facing a severe power bottleneck. Connecting to the traditional grid now takes years, prompting hyperscalers to pioneer a "Bring Your Own Power" (BYOP) movement. Tech giants are directly funding behind-the-meter gas generation, reviving dormant nuclear facilities, and investing in advanced cooling technologies to fuel their server farms. AI infrastructure has become such a critical priority that it is increasingly viewed through the lens of national security, prompting aggressive federal action to expand the domestic supply of key electrical grid components.

On the policy front, the US government has dramatically accelerated its embrace of artificial intelligence. Moving away from more cautious regulatory frameworks, the focus has shifted entirely to removing barriers to innovation and ensuring tech sovereignty. The goal is clear: maintain a decisive strategic edge over global competitors, particularly China. Federal AI spending has skyrocketed into the tens of billions, dominated overwhelmingly by the Department of Defense, which views AI supremacy as a non-negotiable imperative for future military readiness, cybersecurity, and global diplomacy.

However, this hyper-accelerated growth is not without domestic friction. At the local level, the proliferation of massive data centers is creating tension in communities grappling with the environmental footprint of these facilities. Concerns over local electricity rate hikes, immense water usage in water-stressed regions, and the strain on existing utilities highlight the localized costs of a global tech race. Furthermore, while the US excels at rapid technological deployment, the corporate sector is experiencing a deep divide between companies effectively restructuring for an AI-native future and those struggling with high failure rates due to poor data quality and broken processes.

In conclusion, the United States in the age of AI represents a high-stakes, capital-fueled engine of exponential growth. It is a nation betting that its unmatched capacity for private investment, hardware innovation, and sheer ambition can overcome formidable physical bottlenecks. The American trajectory will ultimately determine whether a market-driven society can build and sustain the colossal physical infrastructure required to unlock the next frontier of human intelligence."""
}

result = workflow.invoke(initial_state)

print("result", result)
