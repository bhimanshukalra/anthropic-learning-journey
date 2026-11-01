Structured output often uses a JSON schema to enforce output structure.

from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Literal
from openai import OpenAI

class Mention(BaseModel): # The model chooses the product the mention is about, # as well as the social media post's sentiment
product: Literal['app', 'website', 'not_applicable']
sentiment: Literal['positive', 'negative', 'neutral']

    # Model can choose to respond to the user
    needs_response: bool
    response: Optional[str]

    # If a support ticket needs to be opened,
    # the model can write a description for the
    # developers
    support_ticket_description: Optional[str]

def analyze_mention(
mention: str,
personality: str = "friendly"
) -> Mention:
completion = client.beta.chat.completions.parse(
model="gpt-4o-mini",
messages=[
{"role": "system", "content": f"""
Extract structured information from
social media mentions about our products.

                Provide
                - The product mentioned (website, app, not applicable)
                - The mention sentiment (positive, negative, neutral)
                - Whether to respond (true/false). Don't respond to
                  inflammatory messages or bait.
                - A customized response to send to the user if we need
                  to respond.
                - An optional support ticket description to create.

                Your personality is {personality}.
            """},
            {"role": "user", "content": mention},
        ],
        response_format=Mention,
    )
    return completion.choices[0].message.parsed
