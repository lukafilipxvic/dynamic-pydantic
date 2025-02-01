import os
import requests
from pydantic import BaseModel
import pymupdf4llm
from dynamic_pydantic import dynamic_model
import instructor
from litellm import completion

LLM_MODEL = os.getenv("LLM_MODEL")

class yearsModel(BaseModel):
    calendarYears: list[int]

if __name__ == "__main__":
    pdf_url = "https://www.apple.com/newsroom/pdfs/fy2024-q4/FY24_Q4_Consolidated_Financial_Statements.pdf"
    response = requests.get(pdf_url)
    file_path = "Apple FY24 Q4 Financials.pdf"

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully')
    else:
        print('Failed to download file')

    md_text = pymupdf4llm.to_markdown(doc=file_path)
    print(md_text)

    # Generate model
    genModel = dynamic_model(extract=md_text,
                             prompt='''
                            Create a pydantic model that contains EVERY line item in Apple's Statement of Income.''',
                             iteration=True,
                             llm_model=LLM_MODEL
                             )
    print(f'Generated Schema: {genModel.schema_json()}')

    client = instructor.from_litellm(completion)

    Years = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"Return the calendar years covered in the provided financial statement:",
            },
            {
                "role": "user",
                "content": f"{md_text}",
            }
        ],
        response_model=yearsModel,
        max_retries=8,
        )

    for year in Years.calendarYears:
        resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"You are an advanced financial data extraction tool. You will accurately extract the FY {year} data from the following context to the provided financial data schema:",
            },
            {
                "role": "user",
                "content": f"{md_text}",
            }
        ],
        response_model=genModel,
        max_retries=8,
        )

        print(f'Extracted data: {resp}')
