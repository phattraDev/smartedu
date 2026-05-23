"""
School Bot Backend API
Handles homework, holidays, subscribers, and broadcast notifications.
Bot runs as a background thread in the same process.
"""
import os
import uuid
import threading
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models
import schemas
from database import engine, get_db
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
)

load_dotenv()  # looks in backend/ folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)  # project root

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

# Uploads folder — use mounted disk on Render, local folder otherwise
UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".txt", ".md",
    ".xls", ".xlsx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

def run_bot():
    """Run the Telegram bot in a separate thread alongside the web server."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        print("[BOT] No TELEGRAM_BOT_TOKEN set — bot not started.")
        return

    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bot"))

    try:
        import asyncio
        import bot as school_bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        school_bot.main()
    except Exception as e:
        print(f"[BOT] Failed to start: {e}")


def keep_alive(url: str):
    """Ping the health endpoint every 10 minutes to prevent Render free tier spin-down."""
    import time
    import httpx as _httpx
    while True:
        time.sleep(600)  # 10 minutes
        try:
            _httpx.get(f"{url}/health", timeout=10)
            print("[PING] Keep-alive ping sent.")
        except Exception as e:
            print(f"[PING] Ping failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only start bot thread if RUN_BOT=true
    if os.getenv("RUN_BOT", "false").lower() == "true":
        print("[BOT] Starting Telegram bot thread...")
        bot_thread = threading.Thread(target=run_bot, daemon=True, name="telegram-bot")
        bot_thread.start()
        print("[BOT] Telegram bot thread started.")

        # Self-ping every 10 minutes to prevent Render free tier spin-down
        api_url = os.getenv("API_BASE_URL", "")
        if api_url:
            ping_thread = threading.Thread(target=keep_alive, args=(api_url,), daemon=True, name="keep-alive")
            ping_thread.start()
            print(f"[PING] Keep-alive started → {api_url}/health")
    else:
        print("[BOT] Bot thread disabled (RUN_BOT != true). Run bot.py separately.")
    yield


app = FastAPI(title="School Bot API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your dashboard domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"[LOGIN] username={repr(form_data.username)} password={repr(form_data.password)}")
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

@app.get("/api/classes", response_model=list[schemas.ClassOut])
def list_classes(db: Session = Depends(get_db)):
    """Public endpoint — the bot calls this to show the class picker."""
    return db.query(models.Class).all()


@app.post("/api/classes", response_model=schemas.ClassOut, status_code=201)
def create_class(
    payload: schemas.ClassCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    existing = db.query(models.Class).filter(models.Class.code == payload.code.upper()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Class code already exists")
    cls = models.Class(name=payload.name, code=payload.code.upper())
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls


@app.delete("/api/classes/{class_id}", status_code=204)
def delete_class(class_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    cls = db.query(models.Class).filter(models.Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(cls)
    db.commit()


# ---------------------------------------------------------------------------
# Homework
# ---------------------------------------------------------------------------

def build_file_url(request_base: str, hw: models.Homework) -> str | None:
    if hw.file_path and hw.file_name:
        return f"{request_base}/api/homework/{hw.id}/file"
    return None


@app.post("/api/homework", response_model=schemas.HomeworkOut, status_code=201)
async def submit_homework(
    class_code: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    due_date: str = Form(...),
    submitted_by: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cls = db.query(models.Class).filter(models.Class.code == class_code.upper()).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    file_name = None
    file_path = None

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        # Read and check size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Max 20 MB.")

        # Save with unique name to avoid collisions
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(save_path, "wb") as f:
            f.write(contents)

        file_name = file.filename
        file_path = save_path

    hw = models.Homework(
        class_id=cls.id,
        subject=subject,
        description=description,
        due_date=due_date,
        submitted_by=submitted_by,
        file_name=file_name,
        file_path=file_path,
    )
    db.add(hw)
    db.commit()
    db.refresh(hw)

    return schemas.HomeworkOut(
        id=hw.id,
        subject=hw.subject,
        description=hw.description,
        due_date=hw.due_date,
        submitted_by=hw.submitted_by,
        file_name=hw.file_name,
        file_url=f"{API_BASE_URL}/api/homework/{hw.id}/file" if hw.file_path else None,
        created_at=hw.created_at,
    )


@app.get("/api/homework/{class_code}", response_model=list[schemas.HomeworkOut])
def get_homework(class_code: str, db: Session = Depends(get_db)):
    """Public endpoint — the bot calls this without auth."""
    cls = db.query(models.Class).filter(models.Class.code == class_code.upper()).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    homework = (
        db.query(models.Homework)
        .filter(models.Homework.class_id == cls.id)
        .order_by(models.Homework.created_at.desc())
        .limit(10)
        .all()
    )
    base = API_BASE_URL
    return [
        schemas.HomeworkOut(
            id=hw.id,
            subject=hw.subject,
            description=hw.description,
            due_date=hw.due_date,
            submitted_by=hw.submitted_by,
            file_name=hw.file_name,
            file_url=f"{base}/api/homework/{hw.id}/file" if hw.file_path else None,
            created_at=hw.created_at,
        )
        for hw in homework
    ]


@app.get("/api/homework/{homework_id}/file")
def download_homework_file(homework_id: int, db: Session = Depends(get_db)):
    """Download the attached file for a homework entry."""
    hw = db.query(models.Homework).filter(models.Homework.id == homework_id).first()
    if not hw or not hw.file_path:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(hw.file_path):
        raise HTTPException(status_code=404, detail="File missing from disk")
    return FileResponse(
        path=hw.file_path,
        filename=hw.file_name,
        media_type="application/octet-stream",
    )


@app.delete("/api/homework/{homework_id}", status_code=204)
def delete_homework(homework_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    hw = db.query(models.Homework).filter(models.Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="Homework not found")
    # Delete file from disk too
    if hw.file_path and os.path.exists(hw.file_path):
        os.remove(hw.file_path)
    db.delete(hw)
    db.commit()


# ---------------------------------------------------------------------------
# Holidays
# ---------------------------------------------------------------------------

@app.get("/api/holidays", response_model=list[schemas.HolidayOut])
def list_holidays(db: Session = Depends(get_db)):
    """Public endpoint — the bot calls this without auth."""
    return db.query(models.Holiday).order_by(models.Holiday.start_date).all()


@app.post("/api/holidays", response_model=schemas.HolidayOut, status_code=201)
def create_holiday(
    payload: schemas.HolidayCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    holiday = models.Holiday(**payload.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@app.delete("/api/holidays/{holiday_id}", status_code=204)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()


# ---------------------------------------------------------------------------
# Subscribers (managed by the bot)
# ---------------------------------------------------------------------------

@app.post("/api/subscribers", response_model=schemas.SubscriberOut, status_code=201)
def upsert_subscriber(payload: schemas.SubscriberUpsert, db: Session = Depends(get_db)):
    """Called by the bot when a user sends /start."""
    sub = db.query(models.Subscriber).filter(
        models.Subscriber.telegram_id == payload.telegram_id
    ).first()
    if sub:
        sub.is_active = True
        sub.first_name = payload.first_name
        sub.username = payload.username
        if payload.class_code:
            sub.class_code = payload.class_code.upper()
    else:
        data = payload.model_dump()
        if data.get("class_code"):
            data["class_code"] = data["class_code"].upper()
        sub = models.Subscriber(**data)
        db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


# IMPORTANT: /count must be defined BEFORE /{telegram_id} to avoid being
# swallowed by the dynamic route parameter.
@app.get("/api/subscribers/count")
def subscriber_count(db: Session = Depends(get_db), _=Depends(get_current_user)):
    count = db.query(models.Subscriber).filter(models.Subscriber.is_active == True).count()
    return {"count": count}


@app.get("/api/subscribers", response_model=list[schemas.SubscriberOut])
def list_subscribers(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Dashboard endpoint for admins to view registered Telegram users."""
    return (
        db.query(models.Subscriber)
        .order_by(models.Subscriber.subscribed_at.desc())
        .all()
    )


@app.get("/api/subscribers/{telegram_id}", response_model=schemas.SubscriberOut)
def get_subscriber(telegram_id: str, db: Session = Depends(get_db)):
    """Called by the bot to check if a parent has a registered class."""
    sub = db.query(models.Subscriber).filter(
        models.Subscriber.telegram_id == telegram_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return sub


@app.patch("/api/subscribers/{telegram_id}/class", response_model=schemas.SubscriberOut)
def set_subscriber_class(
    telegram_id: str,
    payload: schemas.SubscriberSetClass,
    db: Session = Depends(get_db),
):
    """Called by the bot when a parent registers or changes their child's class."""
    sub = db.query(models.Subscriber).filter(
        models.Subscriber.telegram_id == telegram_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    cls = db.query(models.Class).filter(
        models.Class.code == payload.class_code.upper()
    ).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    sub.class_code = payload.class_code.upper()
    db.commit()
    db.refresh(sub)
    return sub


@app.patch("/api/subscribers/{telegram_id}/language", response_model=schemas.SubscriberOut)
def set_subscriber_language(
    telegram_id: str,
    payload: schemas.SubscriberSetLanguage,
    db: Session = Depends(get_db),
):
    """Called by the bot when a parent selects or changes their language."""
    if payload.language not in ("en", "km"):
        raise HTTPException(status_code=400, detail="Language must be 'en' or 'km'")
    sub = db.query(models.Subscriber).filter(
        models.Subscriber.telegram_id == telegram_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    sub.language = payload.language
    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------------
# Broadcast
# ---------------------------------------------------------------------------

@app.post("/api/broadcast", response_model=schemas.BroadcastResult)
async def broadcast(
    payload: schemas.BroadcastRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Send a message to all active subscribers via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")

    subscribers = db.query(models.Subscriber).filter(models.Subscriber.is_active == True).all()
    sent_count = 0

    async with httpx.AsyncClient() as client:
        for sub in subscribers:
            try:
                resp = await client.post(
                    f"{TELEGRAM_API}/sendMessage",
                    json={
                        "chat_id": sub.telegram_id,
                        "text": f"📢 *School Announcement*\n\n{payload.message}",
                        "parse_mode": "Markdown",
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    sent_count += 1
                elif resp.status_code == 403:
                    # User blocked the bot — mark inactive
                    sub.is_active = False
            except httpx.RequestError:
                continue

    db.commit()

    # Log the broadcast
    log = models.BroadcastLog(
        message=payload.message,
        sent_by=current_user["username"],
        recipient_count=sent_count,
    )
    db.add(log)
    db.commit()

    return {"sent_to": sent_count, "message": payload.message}


@app.get("/api/broadcast/history")
def broadcast_history(db: Session = Depends(get_db), _=Depends(require_admin)):
    logs = (
        db.query(models.BroadcastLog)
        .order_by(models.BroadcastLog.sent_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": l.id,
            "message": l.message,
            "sent_by": l.sent_by,
            "sent_at": l.sent_at.isoformat(),
            "recipient_count": l.recipient_count,
        }
        for l in logs
    ]


@app.delete("/api/broadcast/history", status_code=204)
def clear_broadcast_history(db: Session = Depends(get_db), _=Depends(require_admin)):
    db.query(models.BroadcastLog).delete()
    db.commit()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.head("/health")
def health_head():
    return {}


# ---------------------------------------------------------------------------
# Start Telegram bot in background thread
# ---------------------------------------------------------------------------

def run_bot():
    """Run the Telegram bot in a separate thread alongside the web server."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        print("[BOT] No TELEGRAM_BOT_TOKEN set — bot not started.")
        return

    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bot"))

    try:
        import asyncio
        import bot as school_bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        school_bot.main()
    except Exception as e:
        print(f"[BOT] Failed to start: {e}")


# ---------------------------------------------------------------------------
# Serve dashboard (must be last — catches all unmatched routes)
# ---------------------------------------------------------------------------

DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard")

if os.path.isdir(DASHBOARD_DIR):
    # Serve static assets (css, js) at /static
    app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")

    @app.get("/")
    def root():
        return FileResponse(os.path.join(DASHBOARD_DIR, "index.html"))
