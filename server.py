import socket
import pickle
from multiprocessing import Process
from multiprocessing import Manager

class SharedObject:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_data(self, new_data):
        self.data = new_data

# Function to create a Manager and return a proxy for a shared object
def create_shared_object(initial_data):
    manager = Manager()
    return manager.Namespace(), SharedObject(initial_data)

# Define a password for one-time use
ONE_TIME_PASSWORD = "secure_password"
class server(dict):
    def __init__(self,host='127.0.0.1', port=65432):
        initial_data = "Initial data."
        _, shared_object = create_shared_object(initial_data)
        
        self['socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self['socket'].bind((host, port))
        self['socket'].listen()

        print("Server listening on {}:{}".format(host, port))

        while True:
            client_socket, addr = self['socket'].accept()
            print('Connection from', addr)
            
            # Start a new process to handle the client
            print("Starting new process for client.")
            client_process = Process(target=self.handle_client, args=(client_socket, shared_object))
            client_process.start()

    def handle_client(self,client_socket, shared_object):
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



if __name__ == '__main__':
    server()
