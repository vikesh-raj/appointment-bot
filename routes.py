from fastapi import APIRouter, HTTPException, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, PlainTextResponse, FileResponse, JSONResponse
from typing import List
from models import Appointment, NewAppointment
import os
import tempfile
from audio_llm import process_audio_appointment_request, generate_audio_response

router = APIRouter()
templates = Jinja2Templates(directory="templates")

appointments = [
    Appointment(
        id=1,
        name="John Doe",  # Renamed from customer_name
        date="2025-03-21",  # Renamed from appointment_date
        time="10:00 AM",  # Renamed from appointment_time
        service="General Consultation",
        number="123-456-7890"  # Renamed from mobile_number
    ),
    Appointment(
        id=2,
        name="Jane Smith",  # Renamed from customer_name
        date="2025-03-21",  # Renamed from appointment_date
        time="02:00 PM",  # Renamed from appointment_time
        service="Follow-up",
        number="987-654-3210"  # Renamed from mobile_number
    )
]

@router.post("/appointments/", response_model=Appointment)
def create_appointment(
    name: str = Form(...),  # Renamed from customer_name
    date: str = Form(...),  # Renamed from appointment_date
    time: str = Form(...),  # Renamed from appointment_time
    service: str = Form(...),
    number: str = Form(...)  # Renamed from mobile_number
):
    appointment_id = len(appointments) + 1
    appointment = Appointment(
        id=appointment_id,
        name=name,  # Renamed from customer_name
        number=number,  # Renamed from mobile_number
        date=date,  # Renamed from appointment_date
        time=time,  # Renamed from appointment_time
        service=service,
    )
    appointments.append(appointment)
    return RedirectResponse(url="/appointments", status_code=303)

@router.get("/appointments/", response_model=List[Appointment])
def get_appointments(request: Request):
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments})

@router.get("/appointments/new")
def new_appointment(request: Request):
    return templates.TemplateResponse("create_appointment.html", {"request": request})

@router.get("/appointments/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int, request: Request):
    for appointment in appointments:
        if appointment.id == appointment_id:
            if request.headers.get("HX-Request"):
                # Return the updated table row partial to swap in inline
                return templates.TemplateResponse("appointment_row.html", {"request": request, "appointment": appointment})
            return RedirectResponse(url="/appointments", status_code=303)
    raise HTTPException(status_code=404, detail="Appointment not found")


@router.post("/appointments/delete/{appointment_id}")
def delete_appointment(appointment_id: int, request: Request):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            del appointments[index]
            if request.headers.get("HX-Request"):
                # Return a plain response to let HTMX remove the deleted row inline
                return PlainTextResponse("Deleted", status_code=200)
            return RedirectResponse(url="/appointments", status_code=303)
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.post("/appointments/{appointment_id}/edit")
def edit_appointment(
    appointment_id: int,
    request: Request,
    name: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    service: str = Form(...),
    number: str = Form(...)
):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index].name = name
            appointments[index].date = date
            appointments[index].time = time
            appointments[index].service = service
            appointments[index].number = number
            if request.headers.get("HX-Request"):
                # Return the updated table row partial to swap in inline
                return templates.TemplateResponse("appointment_row.html", {"request": request, "appointment": appointments[index]})
            return RedirectResponse(url="/appointments", status_code=303)
    raise HTTPException(status_code=404, detail="Appointment not found")

# API Endpoints

@router.get("/api/appointments/", response_model=List[Appointment])
def api_get_all_appointments():
    return appointments

@router.post("/api/appointments/", response_model=Appointment)
def api_create_appointment(
    appointment: NewAppointment,
):
    appointment_id = len(appointments) + 1
    a = Appointment(id=appointment_id, **appointment.dict())
    appointments.append(a)
    return a

@router.get("/api/appointments/{appointment_id}", response_model=Appointment)
def api_get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/api/appointments/{appointment_id}")
def api_delete_appointment(appointment_id: int):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            del appointments[index]
            return appointments[index]
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.put("/api/appointments/{appointment_id}", response_model=Appointment)
def api_update_appointment(appointment_id: int, updated_appointment: Appointment):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

# Audio LLM Endpoints

@router.post("/api/audio/process")
async def process_audio(audio: UploadFile = File(...)):
    """
    Process audio file to create appointment via Audio LLM.
    Transcribes audio, extracts appointment details using LLM, and returns results.
    """
    # Create temp file for uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_audio:
        content = await audio.read()
        temp_audio.write(content)
        temp_audio_path = temp_audio.name
    
    try:
        # Process the audio through the LLM pipeline
        result = process_audio_appointment_request(temp_audio_path)
        
        # If all appointment details are present, create the appointment
        details = result["appointment_details"]
        if all(details.values()):
            appointment_id = len(appointments) + 1
            appointment = Appointment(
                id=appointment_id,
                name=details["name"],
                number=details["number"],
                date=details["date"],
                time=details["time"],
                service=details["service"]
            )
            appointments.append(appointment)
            result["appointment_created"] = True
            result["appointment_id"] = appointment_id
        else:
            result["appointment_created"] = False
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@router.post("/api/audio/tts")
async def text_to_speech(text: str = Form(...)):
    """
    Convert text to speech and return audio file.
    """
    # Create temp file for generated audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        # Generate audio from text
        audio_path = generate_audio_response(text, temp_audio_path)
        
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename="response.mp3"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio")
def audio_interface(request: Request):
    """
    Render the audio LLM interface page.
    """
    return templates.TemplateResponse("audio_llm.html", {"request": request})

@router.put("/api/appointments/{appointment_id}", response_model=Appointment)
def api_update_appointment(appointment_id: int, updated_appointment: Appointment):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")