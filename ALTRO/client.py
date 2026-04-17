import socket


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 65432))

    user = input("Username: ")
    pwd = input("Password: ")
    client.send(f"{user}:{pwd}".encode('utf-8'))

    response = client.recv(1024).decode('utf-8')
    print(f"\n{response}\n")

    if "ERRORE" in response: return

    print("Comandi disponibili: /referente, /lista, !EXIT")
    while True:
        cmd = input(f"({user}) > ")
        client.send(cmd.encode('utf-8'))

        if cmd == "!EXIT": break

        res = client.recv(1024).decode('utf-8')
        print(f"RISPOSTA: {res}\n")

    client.close()


if __name__ == "__main__":
    start_client()