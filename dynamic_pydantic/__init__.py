import os
from pydantic import BaseModel, create_model, Field
from typing import Annotated, Literal
import instructor
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

class Variable(BaseModel):
    name: str
    type: Literal['str', 'int', 'bool', 'float', 'list[str]']
    description: str

class Schema(BaseModel):
    schemaName: str
    variables: list[Variable]
    

client = instructor.from_litellm(completion)

def dynamic_model(
    extract: str = None,
    prompt: str = None,
    iteration: bool = False,
    llm_model: str = os.getenv("LLM_MODEL")
) -> type[BaseModel]:
    """
    Generate Pydantic models dynamically using user-defined prompts and optional extracts.
    """
    # Build the prompt dynamically
    formatted_extract = f"<content>\n{extract}\n</content>" if extract else ''
    default_prompt = """
    You are an advanced schema generation tool designed to create structured Pydantic schemas.
    Generate a schema based on the provided content and guidelines.
    """
    final_prompt = prompt or default_prompt
    complete_prompt = f"""
    {final_prompt}

    {formatted_extract}

    Guidelines for schema generation:
    1. Ensure the schema is complete and accurately represents the user's request.
    2. Use appropriate Pydantic types for each field (e.g., str, int, bool, float, list).
    3. Provide clear and concise field descriptions.
    4. Handle ambiguities by using general best practices.
    5. If the schema should be iterable, ensure the output is a list of schemas.

    Return the most relevant schema based on the user's request.
    """

    resp = client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "system", "content": complete_prompt}],
        response_model=Schema,
    )

    genSchema = resp.model_dump()
    variableSchema = [(var['name'], var['type'], var['description']) for var in genSchema['variables']]

    # Dynamically create the Pydantic model
    generatedSchema = create_model(
        genSchema['schemaName'],
        **{
            property_name: (Annotated[property_type, Field(description=description, default=None)])
            for property_name, property_type, description in variableSchema
        },
        __base__=BaseModel,
    )

    # Iterate the model if required
    if iteration:
        return create_model("StructuredData", data=(list[generatedSchema], ...))
    return generatedSchema

