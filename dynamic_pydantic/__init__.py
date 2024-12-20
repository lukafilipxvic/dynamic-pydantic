import os
from pydantic import BaseModel, create_model, Field
from typing import Annotated, Literal
import instructor
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# Set pydantic models
class Variable(BaseModel):
    name: str
    type: Literal['str', 'int', 'bool', 'float', 'list[str]']
    description: str

class Schema(BaseModel):
    schemaName: str
    variables: list[Variable]
    

# Enable instructor litellm patches 
client = instructor.from_litellm(completion)

# Schema generation
def dynamic_model(extract: str = None, prompt: str = None, iteration: bool = False, llm_model: str = os.getenv("LLM_MODEL")) -> type[BaseModel]:
    '''
    Generate pydantic models dynamically using a prompt and additional extract for context.
    '''
    formatted_extract = f"<content>\n{extract}\n</content>" if extract is not None else ''
    iterate = "The variables must be iterable." if iteration==True else ""

    if not prompt:
        prompt ='''
        <user_request>
        Generate a schema based on the provided extract content.
        </user_request>
        '''

    resp = client.chat.completions.create(
    model=llm_model, 
    messages=[
        {
            "role": "system",
            "content": f'''
            You are an advanced schema generation tool designed to create structured Pydantic schema. Your task is to analyze the provided web extract and generate a schema that accurately represents the data structure.

            {formatted_extract}
            
            {prompt}

            <schema_block>
            {Schema.model_json_schema}
            </schema_block>

            You will return the most relevant Pydantic schema based on the user's request.
            {iterate}

            Guidelines for schema generation:
            1. Ensure that the schema is complete and accurately reflects the data types and structure present in the extract.
            2. Use appropriate Pydantic types for each field (e.g., str, int, list, etc.).
            3. Provide clear and concise descriptions for each field based on the content of the extract.
            4. If the extract is empty or unclear, generate a default schema with common fields based on typical data structures.
            5. If the user has specified that the schema should be iterable, ensure that the output is a list of the generated schema.
            6. Avoid common mistakes such as using incorrect variable types or vague descriptions.

            Before outputting your answer, double-check that the Pydantic schema you are returning is complete and contains the correct information requested by the user. If you encounter any ambiguities, ask clarifying questions to ensure accuracy.
            ''',
        },
    ],
    response_model=Schema,
    )

    genSchema = resp.model_dump()

    variableSchema = [(var['name'], var['type'], var['description']) for var in genSchema['variables']]

    generatedSchema = create_model(
        genSchema['schemaName'],
        **{
            property_name: (Annotated[property_type, Field(description=description, default=None)])
            for property_name, property_type, description in variableSchema
        },
        __base__=BaseModel,
    )
  
    if iteration:   # Turn into list[generatedSchema] for iterable data extraction.
        return create_model("StructuredData",data=(list[generatedSchema], ...))
    return generatedSchema
