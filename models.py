from pydantic import BaseModel
from typing import Optional

class Appointment(BaseModel):
    id: int
    name: str
    number: str
    date: str
    time: str
    service: str

class NewAppointment(BaseModel):
    name: str
    number: str
    date: str
    time: str
    service: str
