from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db
import google.generativeai as genai

app = FastAPI()

# 🛑 Security Note: API Key-ah .env file-la vekkuradhu nalladhu
genai.configure(api_key="AIzaSyDhue3_ca7E-ODpt4kNye-ayUc45tZvdqw")
model = genai.GenerativeModel('gemini-1.5-flash')

# ✅ CORS Settings (Keep this as it is)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "Hospital Backend is Live!"}

# ✅ Change to @app.post because your Frontend uses axios.post
@app.post("/chat")
def hospital_bot(user_msg: str, p_id: str = None, db: Session = Depends(get_db)):
    bot_reply = ""
    user_msg_lower = user_msg.lower()

    # 1. HARD-CODED KEYWORD MAPPING
    if any(word in user_msg_lower for word in ["chest", "heart", "cardio", "breathless"]):
        suggested_specialist = "Cardiologist"
    elif any(word in user_msg_lower for word in ["skin", "rash", "itch", "derma"]):
        suggested_specialist = "Dermatologist"
    elif any(word in user_msg_lower for word in ["bone", "joint", "fracture", "ortho"]):
        suggested_specialist = "Orthopedic"
    elif any(word in user_msg_lower for word in ["stomach", "gastric", "digestion"]):
        suggested_specialist = "Gastroenterologist"
    else:
        # 2. IF NO KEYWORDS, ASK AI
        try:
            prompt = f"Identify the medical specialist for: '{user_msg}'. One word only: [Cardiologist, Dermatologist, Orthopedic, Gastroenterologist, General Physician]."
            response = model.generate_content(prompt)
            suggested_specialist = response.text.strip().replace(".", "").title()
        except:
            suggested_specialist = "General Physician"

    print(f"--- LOGS ---")
    print(f"Input: {user_msg} | Match: {suggested_specialist}")

    # 3. DATABASE QUERY
    doctor = db.query(models.Doctor).filter(
        models.Doctor.specialization.ilike(f"%{suggested_specialist}%")
    ).first()

    if doctor:
        name = doctor.name
        if not name.startswith("Dr."):
            name = f"Dr. {name}"
            
        bot_reply = f"AI analysis suggests a {suggested_specialist}. I recommend consulting {name}."
        print(f"DB Result: Found {doctor.name}")
    else:
        bot_reply = f"AI suggests a {suggested_specialist}. Please consult our General Physician for now."
        print(f"DB Result: NO MATCH FOUND")

    print(f"--- END ---")
    return {"reply": bot_reply}