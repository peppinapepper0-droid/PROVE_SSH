from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import webbrowser
import threading
import time

app = FastAPI(title="PCTO Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    db = client.pcto
    students = db.students
    entities = db.entities
    questionnaires = db.questionnaires
    USE_DB = True
    print("✅ MongoDB connesso")
except Exception as e:
    print(f"⚠️  MongoDB non disponibile, uso dati demo: {e}")
    USE_DB = False

# Demo data fallback
demo_entities = [
    {"name": "Caritas", "contact": "info@caritas.it", "phone": "02-1234567",
     "address": "Via Roma 1, Milano", "sector": "Sociale", "site": "caritas.it",
     "capacity": 5, "tutor": "Mario Rossi", "tutor_phone": "333-1111111",
     "schedule": {"lun": [{"start": "08:00", "end": "12:00"}], "mar": [], "mer": [{"start": "08:00", "end": "12:00"}], "gio": [], "ven": [{"start": "08:00", "end": "12:00"}], "sab": []}},
    {"name": "Legambiente", "contact": "info@legambiente.it", "phone": "02-9876543",
     "address": "Via Verde 5, Milano", "sector": "Ambiente", "site": "legambiente.it",
     "capacity": 4, "tutor": "Laura Bianchi", "tutor_phone": "333-2222222",
     "schedule": {"lun": [{"start": "09:00", "end": "13:00"}], "mar": [{"start": "09:00", "end": "13:00"}], "mer": [], "gio": [{"start": "09:00", "end": "13:00"}], "ven": [], "sab": []}},
    {"name": "Croce Rossa", "contact": "info@cri.it", "phone": "02-5551234",
     "address": "Via Salute 10, Milano", "sector": "Sanitario", "site": "cri.it",
     "capacity": 6, "tutor": "Giulia Verdi", "tutor_phone": "333-3333333",
     "schedule": {"lun": [], "mar": [{"start": "08:00", "end": "14:00"}], "mer": [{"start": "08:00", "end": "14:00"}], "gio": [], "ven": [{"start": "08:00", "end": "14:00"}], "sab": []}},
]
demo_students = []


class EntityModel(BaseModel):
    name: str
    contact: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    sector: Optional[str] = ""
    site: Optional[str] = ""
    capacity: Optional[int] = 0
    tutor: Optional[str] = ""
    tutor_phone: Optional[str] = ""
    school_ref: Optional[str] = ""
    school_ref_phone: Optional[str] = ""
    schedule: Optional[dict] = {}


class PreferencesModel(BaseModel):
    email: str
    choices: List[str]


class AssignModel(BaseModel):
    email: str
    entity: str


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/login.html")


@app.get("/studente")
def student_page():
    return FileResponse("static/studente.html")


@app.get("/scuola")
def school_page():
    return FileResponse("static/scuola.html")


@app.get("/admin")
def admin_page():
    return FileResponse("static/admin.html")


@app.post("/login")
def login(email: str, password: str):
    if USE_DB:
        student = students.find_one({"email": email})
        if not student:
            students.insert_one({"email": email, "password": password, "choices": [], "assigned_entity": None})
    else:
        student = next((s for s in demo_students if s["email"] == email), None)
        if not student:
            demo_students.append({"email": email, "password": password, "choices": [], "assigned_entity": None})
    return {"status": "ok", "email": email}


@app.get("/entities")
def get_entities():
    if USE_DB:
        return list(entities.find({}, {"_id": 0}))
    return demo_entities


@app.post("/entities")
def create_entity(entity: EntityModel):
    data = entity.dict()
    if USE_DB:
        entities.insert_one(data)
    else:
        demo_entities.append(data)
    return {"status": "created"}


@app.put("/entities/{name}")
def update_entity(name: str, entity: EntityModel):
    data = entity.dict()
    if USE_DB:
        entities.update_one({"name": name}, {"$set": data}, upsert=True)
    else:
        idx = next((i for i, e in enumerate(demo_entities) if e["name"] == name), None)
        if idx is not None:
            demo_entities[idx] = data
        else:
            demo_entities.append(data)
    return {"status": "updated"}


@app.delete("/entities/{name}")
def delete_entity(name: str):
    if USE_DB:
        entities.delete_one({"name": name})
    else:
        global demo_entities
        demo_entities = [e for e in demo_entities if e["name"] != name]
    return {"status": "deleted"}


@app.post("/preferences")
def save_preferences(prefs: PreferencesModel):
    if USE_DB:
        students.update_one({"email": prefs.email}, {"$set": {"choices": prefs.choices}})
    else:
        s = next((s for s in demo_students if s["email"] == prefs.email), None)
        if s:
            s["choices"] = prefs.choices
    return {"status": "saved"}


@app.post("/assign")
def assign(data: AssignModel):
    if USE_DB:
        students.update_one({"email": data.email}, {"$set": {"assigned_entity": data.entity}})
    else:
        s = next((s for s in demo_students if s["email"] == data.email), None)
        if s:
            s["assigned_entity"] = data.entity
    return {"status": "assigned"}


@app.get("/assignment/{email}")
def assignment(email: str):
    if USE_DB:
        student = students.find_one({"email": email})
        return {"entity": student.get("assigned_entity") if student else None}
    s = next((s for s in demo_students if s["email"] == email), None)
    return {"entity": s["assigned_entity"] if s else None}


@app.get("/students")
def get_students():
    if USE_DB:
        return list(students.find({}, {"_id": 0, "password": 0}))
    return [{"email": s["email"], "choices": s.get("choices", []), "assigned_entity": s.get("assigned_entity")} for s in demo_students]


@app.get("/stats")
def stats():
    if USE_DB:
        pipeline = [{"$group": {"_id": "$assigned_entity", "count": {"$sum": 1}}}]
        results = list(students.aggregate(pipeline))
    else:
        from collections import Counter
        counts = Counter(s.get("assigned_entity") for s in demo_students if s.get("assigned_entity"))
        results = [{"_id": k, "count": v} for k, v in counts.items()]
    return {"labels": [r["_id"] for r in results if r["_id"]], "values": [r["count"] for r in results if r["_id"]]}


@app.get("/questionnaire_stats")
def questionnaire_stats():
    if USE_DB:
        pipeline = [{"$group": {"_id": "$entity", "avgScore": {"$avg": "$score"}}}]
        results = list(questionnaires.aggregate(pipeline))
        return {"labels": [r["_id"] for r in results], "values": [round(r["avgScore"], 2) for r in results]}
    return {"labels": ["Caritas", "Legambiente", "Croce Rossa"], "values": [72, 85, 61]}


def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀  PCTO Manager avviato!")
    print("="*50)
    print("🌐  Apertura browser automatica...")
    print("📍  URL: http://127.0.0.1:8000")
    print("⏹   Premi CTRL+C per fermare il server")
    print("="*50 + "\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
