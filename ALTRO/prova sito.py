import asyncio
import tornado.web
from motor.motor_tornado import MotorClient

# --- CONFIGURAZIONE ---
PORT = 8080
COOKIE_SECRET = "CHIAVE_MOLTO_LUNGA_E_DIFFICILE_DA_INDOVINARE_998877"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "mio_database"


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        # Tornado distingue automaticamente gli utenti tramite i cookie del loro browser
        user = self.get_secure_cookie("user_email")
        return user.decode() if user else None

    def get_user_role(self):
        role = self.get_secure_cookie("user_role")
        return role.decode() if role else None


# --- GESTIONE AUTENTICAZIONE ---

class RegisterHandler(BaseHandler):
    def get(self):
        self.write('''
            <html><body><h2>Registrazione Studente</h2>
            <form method="post">
                Email: <input type="email" name="email" required><br><br>
                Password: <input type="password" name="password" required><br><br>
                <input type="submit" value="Registrati">
            </form><br><a href="/login">Hai già un account? Accedi</a></body></html>
        ''')

    async def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")

        # Controlla se l'email esiste già
        esistente = await self.db.utenti.find_one({"email": email})
        if esistente:
            self.write("Errore: Email già registrata. <a href='/register'>Riprova</a>")
            return

        # Crea il nuovo utente con ruolo 'studenti'
        nuovo_studente = {
            "email": email,
            "password": password,
            "ruolo": "studenti"
        }
        await self.db.utenti.insert_one(nuovo_studente)
        self.redirect("/login")


class LoginHandler(BaseHandler):
    def get(self):
        # Se un utente è già loggato in questo browser, lo manda alla sua dashboard
        if self.get_current_user():
            self.redirect(f"/{self.get_user_role()}")
            return

        self.write('''
            <html><body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                <h1>Login Multi-Utente</h1>
                <form method="post" style="border:1px solid gray; display:inline-block; padding:20px;">
                    Email: <br><input type="text" name="email"><br><br>
                    Password: <br><input type="password" name="password"><br><br>
                    <input type="submit" value="Entra">
                </form>
                <p><a href="/register">Sei uno studente? Registrati qui</a></p>
            </body></html>
        ''')

    async def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")

        user = await self.db.utenti.find_one({"email": email, "password": password})

        if user:
            # Imposta i cookie per QUESTO specifico browser/utente
            self.set_secure_cookie("user_email", user["email"])
            self.set_secure_cookie("user_role", user["ruolo"])
            self.redirect(f"/{user['ruolo']}")
        else:
            self.write("Credenziali errate. <a href='/login'>Riprova</a>")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user_email")
        self.clear_cookie("user_role")
        self.redirect("/login")


# --- DASHBOARD (Pagine protette) ---

class StudentDash(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        if self.get_user_role() != "studenti":
            self.redirect("/login")
            return
        self.write(f"<h1>Area Studente</h1><p>Benvenuto {self.current_user}!</p><a href='/logout'>Esci</a>")


class ReferentDash(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        if self.get_user_role() != "referente":
            raise tornado.web.HTTPError(403)
        self.write(f"<h1>Area Referente</h1><p>Accesso come: {self.current_user}</p><a href='/logout'>Esci</a>")


class RootDash(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        if self.get_user_role() != "root":
            raise tornado.web.HTTPError(403)
        self.write(f"<h1>Pannello ROOT</h1><p>ID Amministratore: {self.current_user}</p><a href='/logout'>Esci</a>")


# --- AVVIO APP ---

def make_app():
    return tornado.web.Application(
        [
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/register", RegisterHandler),
            (r"/studenti", StudentDash),
            (r"/referente", ReferentDash),
            (r"/root", RootDash),
            (r"/", tornado.web.RedirectHandler, {"url": "/login"}),
        ],
        cookie_secret=COOKIE_SECRET,
        login_url="/login",
        debug=True
    )


async def main():
    app = make_app()
    client = MotorClient(MONGO_URI)
    app.db = client[DB_NAME]
    app.listen(PORT)
    print(f"✅ Server multi-utente attivo su http://localhost:{PORT}")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nArresto...")