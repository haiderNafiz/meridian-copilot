import os
from groq import Groq
from dotenv import load_dotenv  # Added this line

# Load environment variables from the local .env file
load_dotenv() 

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Quick verification test
print("API Key loaded successfully:", "GROQ_API_KEY" in os.environ)


# Implement LLM classifier

import json

from schema import IntentOutput


def classify_with_llm(text: str):

    with open(
        "src/intelligence/tools/intent_classifier/prompt.txt"
    ) as f:

        prompt = f.read()

    prompt = prompt.replace(
        "{{raw_text}}",
        text
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content

    data = json.loads(raw)

    return IntentOutput(**data)