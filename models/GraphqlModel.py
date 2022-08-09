from pydantic import BaseModel, validator

class Item(BaseModel):
    action: str
    input: str
    session_variables: str