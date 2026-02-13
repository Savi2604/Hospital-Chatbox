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
    return {"status": "Hospital Backend is Live with Gemini AI!"}

@app.post("/chat")
def hospital_bot(request: ChatRequest, db: Session = Depends(get_db)):
    user_msg = request.user_msg.strip()
    user_msg_lower = user_msg.lower()

    # ✨ 1. GREETING CHECK (Direct Reply - No Gemini)
    # Hello, Hi-nu sonna direct-ah badhil varum.
    greetings = ["hi", "hello", "hey", "halo", "vanakkam"]
    if any(greet == user_msg_lower for greet in greetings):
        return {"reply": "Hello! I am your AI Hospital Assistant. How can I help you with your symptoms today?"}

    # 2. SMART SPECIALIST SELECTION
    suggested_specialist = None

    # Keyword check (Faster)
    if any(word in user_msg_lower for word in ["chest", "heart", "cardio"]):
        suggested_specialist = "Cardiologist"
    elif any(word in user_msg_lower for word in ["skin", "rash", "itch"]):
        suggested_specialist = "Dermatologist"
    elif any(word in user_msg_lower for word in ["bone", "joint", "fracture"]):
        suggested_specialist = "Orthopedic"
    elif any(word in user_msg_lower for word in ["stomach", "gastric", "digestion"]):
        suggested_specialist = "Gastroenterologist"

    # Keyword illana Gemini kitta help kepom
    if not suggested_specialist:
        try:
            ai_prompt = (
                f"Identify the medical specialty for these symptoms: '{user_msg}'. "
                "Pick the best match from: [Cardiologist, Dermatologist, Orthopedic, Gastroenterologist, General Physician]. "
                "Reply ONLY with the single word specialty name."
            )
            response = model.generate_content(ai_prompt)
            suggested_specialist = response.text.strip().replace(".", "").title()
        except Exception as e:
            # Gemini-la error vandha (404/Invalid Key) General Physician-ku pogaadhu, 
            # badhila advice mattum tharom.
            print(f"Gemini Error: {e}")
            suggested_specialist = "General Physician"

    # 3. DOCTOR SEARCH
    doctor = db.query(models.Doctor).filter(
        models.Doctor.specialization.ilike(f"%{suggested_specialist}%")
    ).first()

    # 4. GET AI-POWERED ADVICE
    try:
        advice_prompt = (
            f"The user has: '{user_msg}'. You suggested a {suggested_specialist}. "
            "Give a very brief medical tip (max 15 words) for this symptom."
        )
        advice_res = model.generate_content(advice_prompt)
        ai_advice = advice_res.text.strip()
    except Exception:
        ai_advice = "Please consult a professional for a detailed checkup."

    # 5. FINAL RESPONSE
    if doctor:
        doc_name = doctor.name if doctor.name.startswith("Dr.") else f"Dr. {doctor.name}"
        bot_reply = f"Based on your symptoms, I recommend seeing a **{suggested_specialist}**. You can consult **{doc_name}** in our hospital.\n\n**Note:** {ai_advice}"
    else:
        bot_reply = f"It seems you should consult a **{suggested_specialist}**. Currently, we don't have this specialist, but our **General Physician** can assist you.\n\n**Note:** {ai_advice}"

    return {"reply": bot_reply}