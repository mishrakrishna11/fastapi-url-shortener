from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from . import models, schemas, utils
from .database import SessionLocal, engine, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency - Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST /shorten - Create short URL
@app.post("/shorten", response_model=schemas.URLInfo)
def create_short_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    short_code = utils.generate_short_code()

    # Make sure short_code is unique
    while db.query(models.URL).filter_by(short_code=short_code).first():
        short_code = utils.generate_short_code()

    new_url = models.URL(
        original_url=str(url.original_url),  # Convert HttpUrl to str
        short_code=short_code
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    response = {
        "id": new_url.id,
        "original_url": new_url.original_url,
        "short_code": new_url.short_code,
        "created_at": new_url.created_at,
        "short_url": f"http://127.0.0.1:8000/{new_url.short_code}"
    }

    return response  # <-- ✅ Properly indented now

# GET /{short_code} - Redirect
@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url = db.query(models.URL).filter_by(short_code=short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url.original_url)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=10000)
