import asyncio
from motor.motor_tornado import MotorClient

# Configurazione (Usa gli stessi dati del server)
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "mio_database"


async def setup_db():
    client = MotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Definiamo gli utenti speciali
    utenti_speciali = [
        {
            "email": "admin@scuola.it",
            "password": "root_password_sicura",
            "ruolo": "root",
            "nome": "Amministratore"
        },
        {
            "   email": "referente@scuola.it",
            "password": "ref_password_sicura",
            "ruolo": "referente",
            "nome": "Prof. Responsabile"
        }
    ]

    print("--- Inizializzazione Database ---")
    for utente in utenti_speciali:
        # Controlla se l'utente esiste già per non duplicarlo
        esistente = await db.utenti.find_one({"email": utente["email"]})
        if not esistente:
            await db.utenti.insert_one(utente)
            print(f"✅ Creato utente {utente['ruolo']}: {utente['email']}")
        else:
            print(f"ℹ️ Utente {utente['ruolo']} già presente, salto l'inserimento.")

    print("--- Operazione completata ---")


if __name__ == "__main__":
    asyncio.run(setup_db())