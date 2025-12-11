# Appointment Bot with Audio LLM

A FastAPI-based appointment booking system for barber shops with AI-powered audio interaction capabilities.

## Features

- **Traditional Web Interface**: Create, view, edit, and delete appointments through a web UI
- **RESTful API**: Full API support for appointment management
- **Audio LLM Integration**: Book appointments using voice commands with AI-powered natural language understanding
  - Speech-to-Text: Converts audio input to text using OpenAI Whisper
  - LLM Processing: Extracts appointment details from natural language using GPT-4o-mini
  - Text-to-Speech: Provides audio responses using OpenAI TTS

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for Audio LLM features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vikesh-raj/appointment-bot.git
cd appointment-bot
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Create a `.env` file with the following variable:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

## Running the Application

Start the server:
```bash
uvicorn main:app --reload
```

Or using justfile:
```bash
just run
```

The application will be available at `http://localhost:8000`

## Usage

### Web Interface

1. **Home Page** (`/`): Landing page with navigation
2. **View Appointments** (`/appointments`): List all appointments
3. **Create Appointment** (`/appointments/new`): Traditional form-based appointment creation
4. **Audio Booking** (`/audio`): Voice-based appointment booking with AI

### Audio LLM Interface

1. Navigate to `/audio`
2. Click "Start Recording" and speak your appointment details
3. Include: name, phone number, date, time, and service type
4. Click "Stop Recording" when done
5. Click "Process Audio" to have AI extract and create the appointment

**Example voice command:**
> "Hi, I'd like to book an appointment. My name is John Doe, my number is 555-123-4567. I need a haircut on December 15th, 2025 at 2:00 PM."

### API Endpoints

#### Standard Endpoints
- `GET /api/appointments/` - Get all appointments
- `POST /api/appointments/` - Create new appointment
- `GET /api/appointments/{id}` - Get specific appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Delete appointment

#### Audio LLM Endpoints
- `POST /api/audio/process` - Process audio file and extract appointment details
  - Accepts: audio file (multipart/form-data)
  - Returns: transcription, appointment details, and confirmation message
- `POST /api/audio/tts` - Convert text to speech
  - Accepts: text (form data)
  - Returns: audio file (MP3)

## Architecture

### Audio LLM Pipeline

1. **Audio Input**: User records audio via browser
2. **Transcription**: Audio is sent to OpenAI Whisper API for transcription
3. **NLU Processing**: Transcribed text is processed by GPT-4o-mini to extract structured appointment data
4. **Appointment Creation**: Extracted details are validated and appointment is created
5. **Audio Response**: Confirmation message is converted to speech using OpenAI TTS

### Technology Stack

- **Backend**: FastAPI (Python)
- **LLM**: OpenAI GPT-4o-mini
- **Speech-to-Text**: OpenAI Whisper
- **Text-to-Speech**: OpenAI TTS
- **Frontend**: Bootstrap, Vanilla JavaScript
- **Templates**: Jinja2

## Development

### Project Structure

```
appointment-bot/
├── main.py              # FastAPI application entry point
├── routes.py            # API routes and web endpoints
├── models.py            # Pydantic models for data validation
├── audio_llm.py         # Audio LLM processing logic
├── templates/           # HTML templates
│   ├── index.html
│   ├── appointments.html
│   ├── create_appointment.html
│   ├── appointment_row.html
│   └── audio_llm.html
├── static/              # Static files
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── justfile            # Build and run commands
```

### Key Components

- **audio_llm.py**: Core Audio LLM functionality
  - `transcribe_audio()`: Convert audio to text
  - `extract_appointment_details()`: Extract structured data using LLM
  - `generate_audio_response()`: Convert text to speech
  - `process_audio_appointment_request()`: Complete pipeline

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
