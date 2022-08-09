from typing import List
from pydantic import BaseModel, validator

class Item(BaseModel):
    action: List
    input: List
    session_variables: List