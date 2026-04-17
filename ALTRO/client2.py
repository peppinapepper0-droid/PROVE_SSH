import socket

HOST = '127.0.0.1'
PORT = 65432


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Fase di Login
    user = input("Username: ")
    pwd = input("Password: ")
    auth_string = f"{user}:{pwd}"
    client.send(auth_string.encode('utf-8'))

    # Riceve responso dal server
    response = client.recv(1024).decode('utf-8')
    print(f"\n[SERVER]: {response}")

    if "ERRORE" in response:
        client.close()
        return

    # Se loggato, può inviare messaggi
    while True:
        msg = input(f"{user}> ")
        client.send(msg.encode('utf-8'))
        if msg == "!DISCONNECT": break

        reply = client.recv(1024).decode('utf-8')
        print(reply)

    client.close()


if __name__ == "__main__":
    start_client()