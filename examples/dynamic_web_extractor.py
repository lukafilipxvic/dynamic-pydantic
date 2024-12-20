# pip install install stealth-requests[parsers]
import os
from stealth_requests import StealthSession
from dynamic_pydantic import dynamic_model
import instructor
from litellm import completion

LLM_MODEL = os.getenv("LLM_MODEL")

def website_to_md(url: str) -> str:
    ''' Extract a website into markdown.'''
    with StealthSession() as session:
        try:
            response = session.get(url)
            response.raise_for_status()
        except Exception as e:
            return f"error: {str(e)}"
    return response.markdown()

if __name__ == "__main__":
    # Extract website
    url = 'https://www.amazon.com/s?k=nvidia+geforce+rtx+4060ti+16gb'
    md_extract = website_to_md(url=url)
    print(md_extract)

    # Generate model
    genModel = dynamic_model(extract=md_extract, prompt='Brand, Product Name, Price', iteration=True, llm_model=LLM_MODEL)
    print(f'Generated Schema: {genModel.schema_json()}')

    # Extract data to generated model
    client = instructor.from_litellm(completion)

    resp = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {
            "role": "system",
            "content": "You are an advanced website structured data extraction tool. You will accurately extract data from the following context to the provided schema:",
        },
        {
            "role": "user",
            "content": f"{md_extract}",
        }
    ],
    response_model=genModel,
    max_retries=5,
    )

    print(f'Extracted website data: {resp}')