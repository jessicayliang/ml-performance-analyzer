from pydantic import BaseModel

class PromptRequest(BaseModel):
    user_id: str
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
