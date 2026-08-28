from openai import OpenAI

from app.config import settings


client = OpenAI(api_key=settings.openai_api_key)

response = client.responses.create(
    model=settings.openai_model,
    input="Reply with exactly: API OK",
)

print(response.output_text)