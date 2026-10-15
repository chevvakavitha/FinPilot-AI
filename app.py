
import os
import json
import streamlit as st
import pandas as pd
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(
    page_title="FinPilot AI",
    page_icon="💼",
    layout="wide"
)

st.title("💼 FinPilot AI")
st.caption("Gemini-Powered Agentic Finance Operations Assistant")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.1-flash-lite"


@st.cache_data
def load_invoices():
    df = pd.read_csv("invoices.csv")
    df["due_date"] = pd.to_datetime(
        df["due_date"], errors="coerce"
    )
    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    ).fillna(0)
    df["paid_amount"] = pd.to_numeric(
        df["paid_amount"], errors="coerce"
    ).fillna(0)
    df["outstanding"] = (
        df["amount"] - df["paid_amount"]
    ).clip(lower=0)
    return df


try:
    invoices = load_invoices()
except Exception as error:
    st.error(f"Could not load invoices.csv: {error}")
    st.stop()

today = pd.Timestamp(date.today())


# Python finance tools

def overdue_invoices():
    data = invoices[
        (invoices["due_date"] < today)
        & (invoices["status"].str.lower() != "paid")
        & (invoices["outstanding"] > 0)
    ]
    return {
        "count": int(len(data)),
        "total_overdue": float(data["outstanding"].sum()),
        "invoices": data.head(100).to_dict(orient="records")
    }


def high_value_overdue(threshold=50000):
    data = invoices[
        (invoices["due_date"] < today)
        & (invoices["status"].str.lower() != "paid")
        & (invoices["outstanding"] > threshold)
    ]
    return {
        "threshold": threshold,
        "count": int(len(data)),
        "total": float(data["outstanding"].sum()),
        "invoices": data.head(100).to_dict(orient="records")
    }


def total_outstanding():
    data = invoices[invoices["status"].str.lower() != "paid"]
    return {
        "total_outstanding": float(data["outstanding"].sum())
    }


def customer_balances():
    data = invoices[invoices["status"].str.lower() != "paid"]
    result = (
        data.groupby("customer")["outstanding"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    return {
        "customers": [
            {"customer": name, "outstanding": float(amount)}
            for name, amount in result.items()
        ]
    }


def overdue_customers():
    data = invoices[
        (invoices["due_date"] < today)
        & (invoices["status"].str.lower() != "paid")
        & (invoices["outstanding"] > 0)
    ]
    result = (
        data.groupby("customer")["outstanding"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    return {
        "customers": [
            {"customer": name, "overdue": float(amount)}
            for name, amount in result.items()
        ]
    }


tool_map = {
    "overdue_invoices": overdue_invoices,
    "high_value_overdue": high_value_overdue,
    "total_outstanding": total_outstanding,
    "customer_balances": customer_balances,
    "overdue_customers": overdue_customers
}


# Gemini function declarations

finance_tools = [
    types.FunctionDeclaration(
        name="overdue_invoices",
        description="Find invoices past their due dates with unpaid balances.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="high_value_overdue",
        description="Find overdue invoices above a specified outstanding amount.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "threshold": types.Schema(
                    type=types.Type.NUMBER,
                    description="Minimum outstanding balance in INR."
                )
            }
        )
    ),
    types.FunctionDeclaration(
        name="total_outstanding",
        description="Calculate total outstanding balance for non-paid invoices.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="customer_balances",
        description="Get the top ten customers by outstanding balance.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    ),
    types.FunctionDeclaration(
        name="overdue_customers",
        description="Get the top ten customers by overdue balance.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={}
        )
    )
]


def ask_finpilot(question):
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=finance_tools)],
        system_instruction=(
            "You are FinPilot AI, a finance operations assistant. "
            "For questions about invoice data, call the appropriate "
            "Python finance tool. Never invent financial figures. "
            "Explain the returned results clearly. Use INR for currency."
        )
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=config
    )

    # Handle a Gemini tool call
    for part in response.candidates[0].content.parts:
        if part.function_call:
            call = part.function_call
            function_name = call.name
            arguments = dict(call.args or {})

            if function_name not in tool_map:
                return "The requested finance tool is unavailable."

            # Execute the actual Python function
            result = tool_map[function_name](**arguments)

            # Send the tool result back to Gemini
            follow_up = client.models.generate_content(
                model=MODEL,
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
                                    response={"result": result}
                                )
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Explain the Python tool result to the user. "
                        "Preserve exact amounts and customer names. "
                        "Do not invent or change financial figures."
                    )
                )
            )

            return (
                f"**Python tool executed:** `{function_name}`\n\n"
                + (follow_up.text or json.dumps(result, default=str))
            )

    return response.text or "I couldn't generate a response."


# Streamlit chat

with st.sidebar:
    st.subheader("Finance Assistant")
    st.markdown(
        "- Overdue invoices\n"
        "- High-value overdue invoices\n"
        "- Total outstanding\n"
        "- Customer balances\n"
        "- Overdue by customer"
    )
    st.caption(f"Invoice records loaded: {len(invoices)}")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm FinPilot AI. Ask me about your overdue "
                "invoices, customer balances, or total outstanding."
            )
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a finance question...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("FinPilot is analyzing your request..."):
            try:
                answer = ask_finpilot(question)
                st.markdown(answer)
            except Exception as error:
                answer = f"An error occurred: {error}"
                st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
