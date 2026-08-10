from langgraph.graph import StateGraph, START, END
from typing import TypedDict


class TemperatureState(TypedDict):
    temp_celsius: float
    temp_fahrenheit: float


def convert_temp(state: TemperatureState) -> TemperatureState:
    celsius = state["temp_celsius"]
    fahrenheit = (celsius * 9 / 5) + 32
    state["temp_fahrenheit"] = round(fahrenheit, 2)

    return state


def main():
    graph = StateGraph(state_schema=TemperatureState)

    graph.add_node("convert_temp", convert_temp)

    graph.add_edge(START, "convert_temp")
    graph.add_edge("convert_temp", END)

    workflow = graph.compile()

    initial_state = {"temp_celsius": 28.5}
    final_state = workflow.invoke(initial_state)
    print(
        "final_state",
        final_state,
    )


if __name__ == "__main__":
    main()
