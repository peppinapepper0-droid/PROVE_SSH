import socket
import threading
import sqlite3

HOST = '127.0.0.1'
PORT = 65432


def ottieni_dati_db(query, params=()):
    conn = sqlite3.connect('utenti.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def handle_client(conn, addr):
    try:
        # 1. Autenticazione (come prima)
        auth_data = conn.recv(1024).decode('utf-8')
        user, pwd = auth_data.split(":")

        res = ottieni_dati_db("SELECT ruolo FROM utenti WHERE username=? AND password=?", (user, pwd))
        if not res:
            conn.send("ERRORE: Credenziali errate.".encode('utf-8'))
            conn.close()
            return

        ruolo = res[0][0]
        conn.send(f"BENVENUTO: Sei loggato come {ruolo.upper()}.".encode('utf-8'))

        # 2. Ciclo Comandi
        while True:
            msg = conn.recv(1024).decode('utf-8').strip()
            if not msg or msg == "!EXIT": break

            # Comando: /chi-e-il-referente (Accessibile a tutti)
            if msg == "/referente":
                ref = ottieni_dati_db("SELECT username FROM utenti WHERE ruolo='referente'")
                conn.send(f"Il referente è: {ref[0][0]}".encode('utf-8'))

            # Comando: /lista (Logica differenziata)
            elif msg == "/lista":
                if ruolo == "studente":
                    conn.send("AZIONE NEGATA: Gli studenti non possono vedere la lista utenti.".encode('utf-8'))

                elif ruolo == "referente":
                    studenti = ottieni_dati_db("SELECT username FROM utenti WHERE ruolo='studente'")
                    lista_nomi = ", ".join([s[0] for s in studenti])
                    conn.send(f"STUDENTI ISCRITTI: {lista_nomi}".encode('utf-8'))

                elif ruolo == "root":
                    tutti = ottieni_dati_db("SELECT username, ruolo FROM utenti")
                    lista_completa = "\n".join([f"- {u[0]} ({u[1]})" for u in tutti])
                    conn.send(f"DATABASE COMPLETO:\n{lista_completa}".encode('utf-8'))

            else:
                conn.send("Comando non riconosciuto. Usa /referente o /lista".encode('utf-8'))

    except Exception as e:
        print(f"Errore con {addr}: {e}")
    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Server in ascolto per richieste autorizzate...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()