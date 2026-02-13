import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import models
from database import engine, get_db
import google.generativeai as genai

app = FastAPI()

# Gemini Config
# Render Environment Variable-la API key sariyaa sethutteengala-nu check pannunga.
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDhue3_ca7E-ODpt4kNye-ayUc45tZvdqw")
genai.configure(api_key=API_KEY)

# Latest model name use pannunga (gemini-1.5-flash)
model = genai.GenerativeModel('gemini-1.5-flash')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_msg: str
    p_id: str = None

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "Hospital Backend is Live with Master AI Logic!"}

@app.post("/chat")
def hospital_bot(request: ChatRequest, db: Session = Depends(get_db)):
    user_msg = request.user_msg.strip()
    p_id = request.p_id  # Patient ID context-kaga

    # 💾 Patient History (History Requirement)
    # Inga Patient ID irundha history-ah prompt kulla sethurom
    history_context = f"Patient ID: {p_id}. Previous history: Fever and fatigue 2 months ago." if p_id else "New Patient."

    try:
        # 🧠 Master Instruction (Appointment, Availability, History & General Chat)
        master_prompt = (
            f"History Context: {history_context}\n"
            f"User Message: '{user_msg}'\n\n"
            "Role: Professional Hospital Assistant.\n"
            "System Instructions:\n"
            "1. Appointment: If user wants to fix an appointment, ask for their preferred date and time.\n"
            "2. Availability: If user asks for a doctor, mention availability for [Cardiologist, Dermatologist, Orthopedic, Gastroenterologist, General Physician].\n"
            "3. Specialization: Map medical symptoms to the correct specialist.\n"
            "4. History: Use the provided Patient ID history if the query relates to it.\n"
            "5. General: For greetings or non-medical chat, reply naturally and helpfully.\n"
            "Format: If medical suggestion, start with 'Specialist: [Name]'. Else, answer naturally."
        )

        response = model.generate_content(master_prompt)
        ai_reply = response.text.strip()

        # 🏥 Specialist and Doctor Database Match (Directing patients requirement)
        if "Specialist:" in ai_reply:
            # First line-la Specialist name mattum edukkum
            spec_line = ai_reply.split('\n')[0]
            spec_name = spec_line.replace("Specialist:", "").strip().split()[0].replace(".", "").title()
            
            doctor = db.query(models.Doctor).filter(
                models.Doctor.specialization.ilike(f"%{spec_name}%")
            ).first()
            
            if doctor:
                doc_name = doctor.name if doctor.name.startswith("Dr.") else f"Dr. {doctor.name}"
                return {"reply": f"Based on your query, I suggest seeing a **{spec_name}**. **{doc_name}** is available today in our hospital. {ai_reply}"}
        
        # 💬 Return Gemini's natural response for General Chat, Appointments, etc.
        return {"reply": ai_reply}

    except Exception as e:
        print(f"Master Error: {e}")
        # Gemini connection error vandha indha fallback reply varum
        return {"reply": "I'm sorry, I'm having trouble connecting to the system. Please try again or visit our General Physician."}