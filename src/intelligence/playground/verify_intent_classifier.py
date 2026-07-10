import asyncio

from src.intelligence.tools.intent_classifier.schema import IntentInput
from src.intelligence.tools.intent_classifier.tool import classify_intent


async def main():

    input_data = IntentInput(
        raw_text="""
        Dear Meridian,

        I would like to apply for your
        Senior Backend Engineer position.

        Please find my resume attached.
        """,

        source="email",

        sender_email="john@example.com"
    )

    result = await classify_intent(input_data)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":

    asyncio.run(main())