# FinPilot AI — Agentic Finance Operations Assistant

An AI-powered finance assistant that uses **Google Gemini, Python, pandas, and Streamlit** to analyze invoice data, identify overdue payments, calculate outstanding balances, and answer finance-related questions through a conversational interface.

## 1. What Is FinPilot AI?

Imagine a company managing hundreds of invoices from different customers. Finance employees may need to filter spreadsheets, calculate unpaid amounts, identify overdue invoices, and determine which customers owe the most money.

FinPilot AI simplifies this analysis. Users ask questions in natural language, the AI can select an appropriate Python finance tool, Python and pandas calculate the results from invoice records, and Gemini explains the results in a readable format.

## 2. How the Project Works

```text
Invoice Dataset (invoices.csv)
             |
             v
Streamlit Chat Interface
             |
             v
User Asks a Finance Question
             |
             v
Google Gemini AI
             |
             v
Selects a Python Finance Tool
             |
             v
Python + pandas
             |
             v
Calculates Results from Invoice Data
             |
             v
Gemini Generates a Natural-Language Answer
             |
             v
Finance Insights Displayed to the User
```

## 3. Key Features

- **Outstanding Balance Analysis:** Calculate the total remaining balance across invoices.
- **Customer Balance Ranking:** Identify customers with the largest outstanding balances.
- **Overdue Customer Analysis:** Rank customers by overdue amounts.
- **Overdue Invoice Detection:** Find invoices past their due dates that still have outstanding balances.
- **High-Value Overdue Analysis:** Identify overdue invoices above a specified amount threshold.
- **Conversational Interface:** Ask finance questions using natural language.
- **AI Tool Calling:** Allow Gemini to select predefined Python functions and use their results to formulate answers.

## 4. The Five Finance Tools

| Tool | Purpose |
|---|---|
| `total_outstanding` | Calculates the total outstanding invoice balance. |
| `customer_balances` | Ranks customers by their outstanding balances. |
| `overdue_customers` | Identifies customers with the highest overdue balances. |
| `overdue_invoices` | Finds overdue invoices with remaining balances. |
| `high_value_overdue` | Finds overdue invoices above a specified threshold. |

The five workflows have been tested locally. The project uses Python functions for financial calculations rather than relying on the language model to perform the arithmetic itself.

## 5. Technology Stack

| Technology | Role |
|---|---|
| Python | Implements finance logic and callable tools. |
| Google Gemini API | Interprets questions and supports AI tool calling. |
| pandas | Loads, filters, groups, and aggregates invoice records. |
| Streamlit | Provides the interactive chat interface. |
| python-dotenv | Loads the API key from a local environment file. |
| CSV | Stores the sample invoice dataset. |

## 6. Project Structure

```text
FinPilot-AI/
├── app.py
├── main.py
├── llm_test.py
├── model_test.py
├── invoices.csv
├── requirements.txt
├── README.md
├── .gitignore
└── .env                 # Private; never upload
```

## 7. Getting Started

### Prerequisites

- Python installed on your computer
- A Google Gemini API key
- Internet access for Gemini API requests

### Installation

**Step 1: Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FinPilot-AI
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL after publishing the project.

**Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 3: Configure the API key**

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own key. Keep `.env` private and do not commit it to GitHub.

**Step 4: Run the application**

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## 8. Example Questions

Try asking the assistant:

- What is the total outstanding balance?
- Which customers have the highest outstanding balances?
- Show all overdue invoices.
- Find overdue invoices above ₹50,000.
- Which customers have the largest overdue balances?

The results depend on the invoice records in `invoices.csv` and the financial rules implemented in the Python tools.

## 9. Is This an Agentic AI Project?

Yes. FinPilot AI demonstrates a basic **single-agent, tool-calling workflow**.

Unlike a simple chatbot that only generates text, the tool-calling implementation can select a predefined finance function, execute it in Python, receive the calculated results, and use those results to formulate an answer.

The current project does not claim multi-agent orchestration, a RAG pipeline, OCR-based invoice extraction, automatic payment processing, or production deployment.

## 10. Business Value

FinPilot AI demonstrates how AI can make routine financial analysis more accessible through natural-language questions.

Potential benefits include:

- Reducing manual spreadsheet filtering and repetitive calculations.
- Helping finance teams identify overdue balances.
- Making customer-level outstanding information easier to explore.
- Providing a foundation for future finance automation.

These are potential benefits; actual time savings and business impact have not yet been measured.

## 11. Current Limitations

- Uses a sample CSV dataset rather than a live accounting system.
- Does not automatically send payment reminders or process transactions.
- Does not predict future payment defaults using a validated predictive model.
- Requires an internet connection and a valid Gemini API key for AI features.
- Has not yet been presented as a production-deployed finance platform.

## 12. Future Improvements

- Add automated unit tests for finance calculations.
- Add customer payment-risk scoring using historical payment data.
- Integrate invoice extraction using OCR.
- Connect to accounting software through secure APIs.
- Add payment reminder workflows with human approval.
- Improve input validation, logging, and error handling.
- Deploy the Streamlit application for a live demonstration.

## 13. Security

- Keep API keys in environment variables or a secrets manager.
- Never upload `.env` or private credentials to GitHub.
- Use synthetic or sanitized data for public demonstrations.
- Apply appropriate access controls before using real financial records.

## 14. Resume Description

**FinPilot AI — Agentic Finance Operations Assistant**

- Developed a Gemini-powered finance assistant using Python, pandas, and Streamlit to analyze invoice records and answer finance-related questions.
- Implemented five callable finance tools for outstanding balance calculation, customer balance ranking, overdue customer analysis, overdue invoice detection, and high-value overdue filtering.
- Integrated Gemini function calling with Python-based financial calculations to generate natural-language responses grounded in computed results.
- Built a conversational interface that enables users to explore invoice data without manually performing every spreadsheet query.

---
