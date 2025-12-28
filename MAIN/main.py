import socket
import threading
import json
from datetime import datetime
import sys

# Server Code
class MessengerServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            client, addr = self.server.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client, addr)).start()
    
    def handle_client(self, client, addr):
        username = client.recv(1024).decode()
        self.clients[username] = client
        print(f"{username} joined from {addr}")
        
        while True:
            try:
                message = client.recv(1024).decode()
                if message:
                    data = json.loads(message)
                    self.broadcast(data, username)
            except:
                del self.clients[username]
                print(f"{username} disconnected")
                break
    
    def broadcast(self, data, sender):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {sender}: {data['message']}"
        
        for user, client in self.clients.items():
            if user != sender:
                try:
                    client.send(message.encode())
                except:
                    pass

# Client Code
class MessengerClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, username):
        self.client.connect((self.host, self.port))
        self.client.send(username.encode())
        print(f"Connected as {username}")
        
        threading.Thread(target=self.receive_messages).start()
        self.send_messages()
    
    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                print(f"\n{message}")
            except:
                break
    
    def send_messages(self):
        while True:
            msg = input("You: ")
            data = json.dumps({"message": msg})
            self.client.send(data.encode())

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = MessengerServer()
        server.start()
    else:
        username = input("Enter username: ")
        client = MessengerClient()
        client.connect(username)