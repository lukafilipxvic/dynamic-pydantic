# Dynamic Pydantic
**Dynamic Pydantic is the easiest way for AI agents to create and validate tools and databases in runtime.**

It is a provides a powerful approach to creating pydantic models dynamically for any given task.

The project leverages Instructor and Pydantic to generate models dynamically based on provided prompt and context.

## Installation
```bash
uv pip install dynamic-pydantic
```

## Contributing
Start contributing by cloning the repository:
```bash
git clone https://github.com/lukafilipxvic/dynamic-pydantic.git
```

## Usage
This package simplifies the interaction between language models and pydantic's ```create_model()``` function.
Below is a basic example showcasing the generation of a Pydantic schema with Cerebras' Llama 3.3 70b inference.

Dynamic Pydantic works with any OpenAI-compatible endpoint via LiteLLM.

```
from dynamic_pydantic import dynamic_model

genModel = dynamic_model(prompt='User = Name, Age')

print(f'{genModel.schema_json()}')

# {"properties": {"Name": {"default": null, "description": "The user's name", "title": "Name", "type": "string"}, "Age": {"default": null, "description": "The user's age", "title": "Age", "type": "integer"}}, "title": "User", "type": "object"}

```

## License
This project is licensed under the terms of the MIT license.

For more details, refer to the LICENSE file in the repository.
