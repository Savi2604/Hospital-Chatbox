import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import models
from database import engine, get_db
import google.generativeai as genai

app = FastAPI()

# 🛑 Render Environment Variable-la irunthu key-ah edukkum. 
# Illana neenga direct-ah kudutha key-ah fallback-ah use pannum.
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
    return {"status": "Hospital Backend is Live!"}

@app.post("/chat")
def hospital_bot(request: ChatRequest, db: Session = Depends(get_db)):
    user_msg = request.user_msg
    user_msg_lower = user_msg.lower()

    # 1. SPECIALIST SELECTION LOGIC
    suggested_specialist = "General Physician"

    if any(word in user_msg_lower for word in ["chest", "heart", "cardio", "breathless"]):
        suggested_specialist = "Cardiologist"
    elif any(word in user_msg_lower for word in ["skin", "rash", "itch", "derma"]):
        suggested_specialist = "Dermatologist"
    elif any(word in user_msg_lower for word in ["bone", "joint", "fracture", "ortho"]):
        suggested_specialist = "Orthopedic"
    elif any(word in user_msg_lower for word in ["stomach", "gastric", "digestion"]):
        suggested_specialist = "Gastroenterologist"
    else:
        try:
            ai_prompt = (
                f"User symptom: '{user_msg}'. From the following list, which specialist should they see? "
                "[Cardiologist, Dermatologist, Orthopedic, Gastroenterologist, General Physician]. "
                "Answer with ONLY the specialist name."
            )
            response = model.generate_content(ai_prompt)
            suggested_specialist = response.text.strip().replace(".", "").title()
        except Exception as e:
            print(f"AI Specialist Error: {e}")

    # 2. DOCTOR SEARCH IN DATABASE
    doctor = db.query(models.Doctor).filter(
        models.Doctor.specialization.ilike(f"%{suggested_specialist}%")
    ).first()

    # 3. GET HELPFUL ADVICE FROM GEMINI (Related Answer)
    try:
        advice_prompt = (
            f"The user has symptoms: '{user_msg}'. They are being referred to a {suggested_specialist}. "
            "Give one very short, helpful medical tip (under 15 words) for this symptom."
        )
        advice_res = model.generate_content(advice_prompt)
        ai_advice = advice_res.text.strip()
    except Exception as e:
        print(f"AI Advice Error: {e}")
        ai_advice = "Stay hydrated and rest until you see a doctor."

    # 4. FINAL REPLY
    if doctor:
        doc_name = doctor.name if doctor.name.startswith("Dr.") else f"Dr. {doctor.name}"
        bot_reply = f"AI analysis suggests a {suggested_specialist}. I recommend consulting {doc_name}. \n\nTip: {ai_advice}"
    else:
        bot_reply = f"AI suggests a {suggested_specialist}. We don't have a specialist available right now. Please consult our General Physician. \n\nTip: {ai_advice}"

    return {"reply": bot_reply}