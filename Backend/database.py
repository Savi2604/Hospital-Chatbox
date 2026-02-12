from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import urllib.parse  # Special characters-ah handle panna ithu mukkiyam

# 1. Unga password-ah inga variable-la vaiyunga
raw_password = "admin@123"

# 2. Password-la irukura '@' symbol-ah safe-ana format-ku mathurom
safe_password = urllib.parse.quote_plus(raw_password)

# 3. Ippo URL-ah build panrom
# Local development-ku intha format
LOCAL_DATABASE_URL = f"postgresql://postgres:{safe_password}@localhost/hospital_db"

# Render-la DATABASE_URL variable irundha adhai edukum, illana local-ah edukum
# Render-la 'postgres://' nu start aana adhai 'postgresql://' nu automatic-ah mathura fix-um sethuruken (Hosting-ku ithu romba mukkiyam)
DATABASE_URL = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()