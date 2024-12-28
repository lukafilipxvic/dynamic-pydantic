import os
from dynamic_pydantic import dynamic_model

from pydantic_ai import Agent

LLM_MODEL = os.getenv("LLM_MODEL")

# Using pydanitc-ai's example
MyModel = dynamic_model(prompt='city str, country str', llm_model=LLM_MODEL)

model = 'groq:llama-3.3-70b-versatile'
print(f'Using model: {model}')
agent = Agent(model, result_type=MyModel)

if __name__ == '__main__':
    result = agent.run_sync('The mile high city in the US of A.')
    print(result.data)
    print(result.usage())