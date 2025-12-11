import os
import json
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file to text using OpenAI Whisper API.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Transcribed text
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")

def extract_appointment_details(text: str) -> Dict[str, Optional[str]]:
    """
    Use OpenAI LLM to extract appointment details from natural language text.
    
    Args:
        text: Natural language text containing appointment information
        
    Returns:
        Dictionary with appointment details (name, number, date, time, service)
    """
    system_prompt = """You are an AI assistant for a barber shop appointment system. 
Extract appointment details from the user's message. Return a JSON object with these fields:
- name: customer's full name
- number: phone number (format: XXX-XXX-XXXX)
- date: appointment date (format: YYYY-MM-DD)
- time: appointment time (format: HH:MM AM/PM)
- service: type of service requested

If any field cannot be determined from the message, set it to null.
Only return the JSON object, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        raise Exception(f"Error extracting appointment details: {str(e)}")

def generate_audio_response(text: str, output_path: str) -> str:
    """
    Generate audio response from text using OpenAI TTS API.
    
    Args:
        text: Text to convert to speech
        output_path: Path where the audio file should be saved
        
    Returns:
        Path to the generated audio file
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Error generating audio response: {str(e)}")

def process_audio_appointment_request(audio_file_path: str) -> Dict:
    """
    Complete pipeline: transcribe audio, extract appointment details, 
    and generate confirmation message.
    
    Args:
        audio_file_path: Path to the audio file with appointment request
        
    Returns:
        Dictionary with transcription, extracted details, and response message
    """
    # Transcribe audio
    transcription = transcribe_audio(audio_file_path)
    
    # Extract appointment details
    appointment_details = extract_appointment_details(transcription)
    
    # Generate confirmation message
    if all(appointment_details.values()):
        response_text = f"I've scheduled an appointment for {appointment_details['name']} on {appointment_details['date']} at {appointment_details['time']} for {appointment_details['service']}. We'll contact you at {appointment_details['number']} if needed."
    else:
        missing_fields = [k for k, v in appointment_details.items() if v is None]
        response_text = f"I need some more information to complete your appointment. Please provide: {', '.join(missing_fields)}."
    
    return {
        "transcription": transcription,
        "appointment_details": appointment_details,
        "response_message": response_text
    }
