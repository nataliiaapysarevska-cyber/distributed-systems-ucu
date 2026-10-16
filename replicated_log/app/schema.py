from pydantic import BaseModel

class Message(BaseModel):
    message: str
    write_concern: int

class ReplicatedMessage(BaseModel):
    message: str
    sequence: int