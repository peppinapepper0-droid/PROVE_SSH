import asyncio
import json
import webbrowser
import tornado.web
import tornado.ioloop
from pymongo import AsyncMongoClient

# ──────────────────────────────────────────────
# Connessione MongoDB asincrona (come nell'esercizio)
# ──────────────────────────────────────────────
client = AsyncMongoClient('localhost', 27017)
db = client["pcto"]
students_collection    = db["students"]
entities_collection    = db["entities"]
questionnaires_collection = db["questionnaires"]


# ──────────────────────────────────────────────
# Base Handler: CORS + JSON helpers
# ──────────────────────────────────────────────
class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Content-Type", "application/json")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def send_json(self, data):
        self.write(json.dumps(data, ensure_ascii=False))

    def get_json_body(self):
        try:
            return json.loads(self.request.body)
        except Exception:
            return {}


# ──────────────────────────────────────────────
# Pagine HTML
# ──────────────────────────────────────────────
class LoginPageHandler(tornado.web.RequestHandler):
    async def get(self):
        with open("static/login.html", "r", encoding="utf-8") as f:
            self.set_header("Content-Type", "text/html")
            self.write(f.read())

class StudentePageHandler(tornado.web.RequestHandler):
    async def get(self):
        with open("static/studente.html", "r", encoding="utf-8") as f:
            self.set_header("Content-Type", "text/html")
            self.write(f.read())

class ScuolaPageHandler(tornado.web.RequestHandler):
    async def get(self):
        with open("static/scuola.html", "r", encoding="utf-8") as f:
            self.set_header("Content-Type", "text/html")
            self.write(f.read())

class AdminPageHandler(tornado.web.RequestHandler):
    async def get(self):
        with open("static/admin.html", "r", encoding="utf-8") as f:
            self.set_header("Content-Type", "text/html")
            self.write(f.read())


# ──────────────────────────────────────────────
# /login  — POST
# ──────────────────────────────────────────────
class LoginHandler(BaseHandler):
    async def post(self):
        email    = self.get_argument("email", "")
        password = self.get_argument("password", "")
        if not email:
            self.set_status(400)
            self.send_json({"error": "email obbligatoria"})
            return
        student = await students_collection.find_one({"email": email})
        if not student:
            await students_collection.insert_one({
                "email": email,
                "password": password,
                "choices": [],
                "assigned_entity": None
            })
        self.send_json({"status": "ok", "email": email})


# ──────────────────────────────────────────────
# /entities  — GET lista, POST crea
# ──────────────────────────────────────────────
class EntitiesHandler(BaseHandler):
    async def get(self):
        result = []
        async for entity in entities_collection.find({}, {"_id": 0}):
            result.append(entity)
        self.send_json(result)

    async def post(self):
        data = self.get_json_body()
        if not data.get("name"):
            self.set_status(400)
            self.send_json({"error": "nome obbligatorio"})
            return
        await entities_collection.insert_one(data)
        self.send_json({"status": "created"})


# ──────────────────────────────────────────────
# /entities/<nome>  — PUT modifica, DELETE elimina
# ──────────────────────────────────────────────
class EntityHandler(BaseHandler):
    async def put(self, name):
        data = self.get_json_body()
        await entities_collection.update_one(
            {"name": name},
            {"$set": data},
            upsert=True
        )
        self.send_json({"status": "updated"})

    async def delete(self, name):
        await entities_collection.delete_one({"name": name})
        self.send_json({"status": "deleted"})


# ──────────────────────────────────────────────
# /preferences  — POST salva preferenze studente
# ──────────────────────────────────────────────
class PreferencesHandler(BaseHandler):
    async def post(self):
        data    = self.get_json_body()
        email   = data.get("email", "")
        choices = data.get("choices", [])
        await students_collection.update_one(
            {"email": email},
            {"$set": {"choices": choices}}
        )
        self.send_json({"status": "saved"})


# ──────────────────────────────────────────────
# /assign  — POST assegna ente a studente
# ──────────────────────────────────────────────
class AssignHandler(BaseHandler):
    async def post(self):
        data   = self.get_json_body()
        email  = data.get("email", "")
        entity = data.get("entity", "")
        await students_collection.update_one(
            {"email": email},
            {"$set": {"assigned_entity": entity if entity else None}}
        )
        self.send_json({"status": "assigned"})


# ──────────────────────────────────────────────
# /assignment/<email>  — GET ente assegnato
# ──────────────────────────────────────────────
class AssignmentHandler(BaseHandler):
    async def get(self, email):
        student = await students_collection.find_one({"email": email})
        entity  = student.get("assigned_entity") if student else None
        self.send_json({"entity": entity})


# ──────────────────────────────────────────────
# /students  — GET lista studenti
# ──────────────────────────────────────────────
class StudentsHandler(BaseHandler):
    async def get(self):
        result = []
        async for s in students_collection.find({}, {"_id": 0, "password": 0}):
            result.append(s)
        self.send_json(result)


# ──────────────────────────────────────────────
# /stats  — GET studenti per ente (aggregazione)
# ──────────────────────────────────────────────
class StatsHandler(BaseHandler):
    async def get(self):
        pipeline = [
            {"$group": {"_id": "$assigned_entity", "count": {"$sum": 1}}}
        ]
        labels, values = [], []
        async for r in students_collection.aggregate(pipeline):
            if r["_id"]:
                labels.append(r["_id"])
                values.append(r["count"])
        self.send_json({"labels": labels, "values": values})


# ──────────────────────────────────────────────
# /questionnaire_stats  — GET punteggi medi
# ──────────────────────────────────────────────
class QuestionnaireStatsHandler(BaseHandler):
    async def get(self):
        pipeline = [
            {"$group": {"_id": "$entity", "avgScore": {"$avg": "$score"}}}
        ]
        labels, values = [], []
        async for r in questionnaires_collection.aggregate(pipeline):
            if r["_id"]:
                labels.append(r["_id"])
                values.append(round(r["avgScore"], 2))
        if not labels:
            labels = ["Caritas", "Legambiente", "Croce Rossa"]
            values = [72, 85, 61]
        self.send_json({"labels": labels, "values": values})


# ──────────────────────────────────────────────
# make_app: tutte le route (come nell'esercizio)
# ──────────────────────────────────────────────
def make_app():
    return tornado.web.Application(
        [
            # Pagine HTML
            (r"/",           LoginPageHandler),
            (r"/studente",   StudentePageHandler),
            (r"/scuola",     ScuolaPageHandler),
            (r"/admin",      AdminPageHandler),

            # API
            (r"/login",                    LoginHandler),
            (r"/entities",                 EntitiesHandler),
            (r"/entities/([^/]+)",         EntityHandler),
            (r"/preferences",              PreferencesHandler),
            (r"/assign",                   AssignHandler),
            (r"/assignment/([^/]+)",       AssignmentHandler),
            (r"/students",                 StudentsHandler),
            (r"/stats",                    StatsHandler),
            (r"/questionnaire_stats",      QuestionnaireStatsHandler),

            # CSS e file statici
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        ],
        debug=True
    )


# ──────────────────────────────────────────────
# Main asincrono (come nell'esercizio)
# ──────────────────────────────────────────────
async def main():
    app = make_app()
    app.listen(8000)

    print("\n" + "=" * 50)
    print("🚀  PCTO Manager avviato con Tornado!")
    print("=" * 50)
    print("🌐  URL: http://127.0.0.1:8000")
    print("⏹   Premi CTRL+C per fermare")
    print("=" * 50 + "\n")

    asyncio.get_event_loop().call_later(1.2, lambda: webbrowser.open("http://127.0.0.1:8000"))

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
