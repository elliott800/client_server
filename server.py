import socket
import pickle
from multiprocessing import Process
from shared_object import create_shared_object

# Define a password for one-time use
ONE_TIME_PASSWORD = "secure_password"

def handle_client(client_socket, shared_object):
    print("Waiting for password from client.")
    # Password check
    password = client_socket.recv(1024).decode()
    print("Received password.")
    
    if password != ONE_TIME_PASSWORD:
        print("Authentication failed for client.")
        client_socket.send("Authentication failed.".encode())
        client_socket.close()
        return
    else:
        client_socket.send("SUCCESS".encode())

    print("Authenticated client.")

    while True:
        command_data = client_socket.recv(1024).decode()
        if not command_data:
            break
        
        parts = command_data.split(" ")
        command = parts[0].upper()

        if command == "GET":
            response = shared_object.get_data()
        elif command == "SET" and len(parts) > 1:
            new_data = ' '.join(parts[1:])
            shared_object.set_data(new_data)
            response = "Data updated."
        else:
            response = "Invalid command."

        client_socket.send(response.encode())

    client_socket.close()

def start_server(host='127.0.0.1', port=65432):
    initial_data = "Initial data."
    _, shared_object = create_shared_object(initial_data)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print("Server listening on {}:{}".format(host, port))

    while True:
        client_socket, addr = server_socket.accept()
        print('Connection from', addr)
        
        # Start a new process to handle the client
        print("Starting new process for client.")
        client_process = Process(target=handle_client, args=(client_socket, shared_object))
        client_process.start()

if __name__ == '__main__':
    start_server()
