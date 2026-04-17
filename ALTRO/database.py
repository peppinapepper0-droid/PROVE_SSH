import sqlite3


def setup_db():
    conn = sqlite3.connect('utenti.db')
    cursor = conn.cursor()

    # Creazione tabella utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            username TEXT PRIMARY KEY,
            password TEXT,
            ruolo TEXT
        )
    ''')

    # Dati di esempio (Username, Password, Ruolo)
    users = [
        ('admin', 'root123', 'root'),
        ('mario_rossi', 'pass123', 'studente'),
        ('luca_verdi', 'referente78', 'referente'),
        ('anna_neri', 'studente456', 'studente'),
        ('pirro_ferrino', 'studente677', 'studente'),
        ('pluto_sorani', 'studente936', 'studente'),
        ('alice_fabio', 'studente648', 'studente'),
        ('paolo_chiara', 'studente172', 'studente'),
        ('ciccio_pasticcio', 'studente620', 'studente')
    ]

    cursor.executemany('INSERT OR IGNORE INTO utenti VALUES (?,?,?)', users)
    conn.commit()
    conn.close()
    print("Database configurato con successo.")


if __name__ == "__main__":
    setup_db()