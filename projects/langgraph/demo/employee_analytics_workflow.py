from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class EmployeeState(TypedDict):
    employee_name: str
    monthly_salary: int
    working_days: int
    completed_projects: int

    yearly_salary: int
    bonus_amount: int
    project_status: str
    summary: str


def calculate_yearly_salary(state: EmployeeState):
    yearly_salary = state["monthly_salary"] * 12
    return {"yearly_salary": yearly_salary}


def calculate_bonus(state: EmployeeState):
    bonus_amount = state["monthly_salary"] * 2
    return {"bonus_amount": bonus_amount}


def project_evaluation(state: EmployeeState):
    if state["completed_projects"] >= 5:
        project_status = "Excellent"
    else:
        project_status = "Excellent"

    return {"project_status": project_status}


def summary(state: EmployeeState):
    summary_text = f"Employee {state['employee_name']} has a yearly salary of {state['yearly_salary']} and a bonus of {state['bonus_amount']}. Project status is {state['project_status']}."
    return {"summary": summary_text}


graph = StateGraph(EmployeeState)

graph.add_node("calculate_yearly_salary", calculate_yearly_salary)
graph.add_node("calculate_bonus", calculate_bonus)
graph.add_node("project_evaluation", project_evaluation)
graph.add_node("summary", summary)

graph.add_edge(START, "calculate_yearly_salary")
graph.add_edge(START, "calculate_bonus")
graph.add_edge(START, "project_evaluation")
graph.add_edge("calculate_yearly_salary", "summary")
graph.add_edge("calculate_bonus", "summary")
graph.add_edge("project_evaluation", "summary")
graph.add_edge("summary", END)

workflow = graph.compile()

initial_state = {
    "employee_name": "John Doe",
    "monthly_salary": 10,
    "working_days": 26,
    "completed_projects": 7,
}

result = workflow.invoke(initial_state)

print("result", result)
