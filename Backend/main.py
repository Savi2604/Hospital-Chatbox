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

    try:
        # 🧠 GEMINI DECISION MAKING
        # Inga Gemini kitta namma instruction kudukkurom: 
        # Specialist thevai na 'Specialist: [Name]' nu thara solrom, illana direct answer solla solrom.
        ai_brain_prompt = (
            f"You are a helpful AI Hospital Assistant. User says: '{user_msg}'. "
            "If they are asking about medical symptoms or seeking a doctor, "
            "reply ONLY in this format: 'Specialist: [Name] | Advice: [Short Tip]'. "
            "Use one of these: [Cardiologist, Dermatologist, Orthopedic, Gastroenterologist, General Physician]. "
            "If they are asking general questions, greetings, or anything else, just reply naturally like a friend."
        )
        
        response = model.generate_content(ai_brain_prompt)
        ai_reply = response.text.strip()

        # 🏥 MEDICAL QUERY CHECK
        if ai_reply.startswith("Specialist:"):
            # Splitting the response to get Specialist and Advice
            # Format: Specialist: Cardiologist | Advice: Keep calm.
            parts = ai_reply.split("|")
            spec_name = parts[0].replace("Specialist:", "").strip().replace(".", "").title()
            ai_advice = parts[1].replace("Advice:", "").strip() if len(parts) > 1 else "Consult a doctor."

            # Database-la Doctor search
            doctor = db.query(models.Doctor).filter(
                models.Doctor.specialization.ilike(f"%{spec_name}%")
            ).first()

            if doctor:
                doc_name = doctor.name if doctor.name.startswith("Dr.") else f"Dr. {doctor.name}"
                return {"reply": f"I suggest consulting a **{spec_name}**. You can meet **{doc_name}** in our hospital.\n\n**Note:** {ai_advice}"}
            else:
                return {"reply": f"It seems you need a **{spec_name}**. We don't have this specialist currently, but our **General Physician** can assist you.\n\n**Note:** {ai_advice}"}
        
        # 💬 GENERAL CHAT REPLY
        # Medical query illana, Gemini kudutha direct answer-ah apdiye anupuvom
        else:
            return {"reply": ai_reply}

    except Exception as e:
        print(f"Gemini Error: {e}")
        # Error vandha fallback to basic greeting
        return {"reply": "I am your AI Hospital Assistant. How can I help you with your symptoms today?"}