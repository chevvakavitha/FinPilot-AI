
import os
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

invoices = pd.read_csv("invoices.csv")
invoices["due_date"] = pd.to_datetime(
    invoices["due_date"], errors="coerce"
)
today = pd.Timestamp(date.today())


def prepare_data():
    data = invoices.copy()
    data["amount"] = pd.to_numeric(
        data["amount"], errors="coerce"
    ).fillna(0)
    data["paid_amount"] = pd.to_numeric(
        data["paid_amount"], errors="coerce"
    ).fillna(0)
    data["outstanding"] = (
        data["amount"] - data["paid_amount"]
    ).clip(lower=0)
    return data


def get_overdue_invoices():
    data = prepare_data()
    return data[
        (data["due_date"] < today)
        & (data["status"].str.lower() != "paid")
        & (data["outstanding"] > 0)
    ]


def get_high_value_overdue(threshold: float = 50000):
    overdue = get_overdue_invoices()
    return overdue[overdue["outstanding"] > threshold]


def get_total_outstanding():
    data = prepare_data()
    return data.loc[
        data["status"].str.lower() != "paid",
        "outstanding"
    ].sum()


def get_customer_outstanding():
    data = prepare_data()
    data = data[data["status"].str.lower() != "paid"]
    return (
        data.groupby("customer")["outstanding"]
        .sum()
        .sort_values(ascending=False)
    )


def get_overdue_by_customer():
    overdue = get_overdue_invoices()
    return (
        overdue.groupby("customer")["outstanding"]
        .sum()
        .sort_values(ascending=False)
    )


def overdue_tool():
    results = get_overdue_invoices()
    return {
        "count": int(len(results)),
        "total_overdue": float(results["outstanding"].sum()),
        "invoices": results.to_dict(orient="records")
    }


def high_value_tool(threshold: float = 50000):
    results = get_high_value_overdue(threshold)
    return {
        "threshold": threshold,
        "count": int(len(results)),
        "invoices": results.to_dict(orient="records")
    }


def total_outstanding_tool():
    return {"total_outstanding": float(get_total_outstanding())}


def customer_balances_tool():
    results = get_customer_outstanding().head(10)
    return {
        "customers": [
            {"customer": name, "outstanding": float(amount)}
            for name, amount in results.items()
        ]
    }


def overdue_customers_tool():
    results = get_overdue_by_customer().head(10)
    return {
        "customers": [
            {"customer": name, "overdue": float(amount)}
            for name, amount in results.items()
        ]
    }


tools = [
    types.FunctionDeclaration(
        name="overdue_invoices",
        description="Get invoices past their due date with an outstanding balance.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="high_value_overdue",
        description="Find overdue invoices whose outstanding balance exceeds a threshold.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "threshold": types.Schema(
                    type=types.Type.NUMBER,
                    description="Minimum outstanding amount in INR."
                )
            }
        )
    ),
    types.FunctionDeclaration(
        name="total_outstanding",
        description="Calculate the total outstanding balance across non-paid invoices.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="customer_balances",
        description="Get the top 10 customers by outstanding balance.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="overdue_customers",
        description="Get the top 10 customers by overdue balance.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    )
]

tool_map = {
    "overdue_invoices": overdue_tool,
    "high_value_overdue": high_value_tool,
    "total_outstanding": total_outstanding_tool,
    "customer_balances": customer_balances_tool,
    "overdue_customers": overdue_customers_tool
}


def answer_question(question):
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=tools)],
        system_instruction=(
            "You are FinPilot AI, a finance operations assistant. "
            "Use the provided functions for questions about invoice data. "
            "Never invent financial figures. Explain tool results clearly."
        )
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=question,
            config=config
        )

        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_name = part.function_call.name
                arguments = dict(part.function_call.args or {})

                if function_name not in tool_map:
                    print("Unknown finance tool requested.")
                    return

                result = tool_map[function_name](**arguments)

                print(f"\n[AGENT TOOL CALLED]: {function_name}")

                follow_up = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part(text=question)]
                        ),
                        response.candidates[0].content,
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_name,
                                        response=result
                                    )
                                )
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "Explain the supplied finance tool results. "
                            "Preserve exact numbers and customer names. "
                            "Do not invent figures."
                        )
                    )
                )

                print("\nFinPilot AI:")
                print(follow_up.text)
                return

        print("\nFinPilot AI:")
        print(response.text)

    except Exception as error:
        print("\nError:", error)


print("===== FINPILOT AI =====")
print("Gemini Agentic Finance Assistant")
print("Try: Show overdue invoices")
print("Try: Show high-value overdue invoices above 50000")
print("Try: What is the total outstanding amount?")
print("Try: Show customer outstanding balances")
print("Try: Show overdue by customer")
print("Type 'exit' to quit.")

while True:
    question = input("\nYour question: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if question:
        answer_question(question)
