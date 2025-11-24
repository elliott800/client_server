import socket
class client(dict):
    def __init__(self,host='127.0.0.1', port=65432):
        self['socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self['socket'].connect((host, port))
        # Send the password first
        password = 'secure_password'#input("Enter the password to connect: ")
        self['socket'].send(password.encode())
        # Wait for authentication response
        auth_response = self['socket'].recv(1024).decode()
        if auth_response == "Authentication failed.":
            print(auth_response)
            self['socket'].close()
            return
        print("Authenticated successfully.")
        '''
        while True:
            command = input("Enter command (GET/SET <data> or EXIT to quit): ")
            if command.upper() == "EXIT":
                break
            self['socket'].send(command.encode())
            # Receive the response
            response = self['socket'].recv(1024).decode()
            print("Response from server:", response)
        self['socket'].close()
        '''
    def get(self):
        command = "GET"
        self['socket'].send(command.encode())
        response = self['socket'].recv(1024).decode()
        print("Response from server:", response)
        return response
    def set(self, new_data):
        command = "SET " + new_data
        self['socket'].send(command.encode())
        response = self['socket'].recv(1024).decode()
        print("Response from server:", response)
        return response

if __name__ == '__main__':
    client()
