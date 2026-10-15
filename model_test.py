
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

models_to_test = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash"
]

for model in models_to_test:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with: FinPilot AI is ready."
        )
        print(f"\nWORKING MODEL: {model}")
        print(response.text)
        break
    except Exception as error:
        print(f"\n{model} failed: {error}")
