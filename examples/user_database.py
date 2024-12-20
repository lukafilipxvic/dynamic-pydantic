import os
from dynamic_pydantic import dynamic_model

genModel = dynamic_model(prompt='User Database = Name, Username, Email, and ID', llm_model=os.getenv("LLM_MODEL"))

print(f'Generated Schema: {genModel.schema_json()}')