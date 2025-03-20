from pydantic import BaseModel

class Appointment(BaseModel):
    id: int
    name: str
    number: str
    date: str
    time: str
    service: str
