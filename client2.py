import socket

HOST = '127.0.0.1'
PORT = 65432


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Connesso al server. Scrivi qualcosa (o '!DISCONNECT' per uscire).")

    while True:
        msg = input("Tu: ")
        client.send(msg.encode('utf-8'))

        if msg == "!DISCONNECT":
            break

        data = client.recv(1024).decode('utf-8')
        print(f"Server: {data}")

    client.close()


if __name__ == "__main__":
    start_client()