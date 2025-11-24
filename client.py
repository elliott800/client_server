import socket

def connect_to_server(host='127.0.0.1', port=65432):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Send the password first
    password = 'secure_password'#input("Enter the password to connect: ")
    client_socket.send(password.encode())

    # Wait for authentication response
    auth_response = client_socket.recv(1024).decode()
    if auth_response == "Authentication failed.":
        print(auth_response)
        client_socket.close()
        return

    print("Authenticated successfully.")

    while True:
        command = input("Enter command (GET/SET <data> or EXIT to quit): ")
        
        if command.upper() == "EXIT":
            break
        
        client_socket.send(command.encode())
        
        # Receive the response
        response = client_socket.recv(1024).decode()
        print("Response from server:", response)

    client_socket.close()

if __name__ == '__main__':
    connect_to_server()
