import socket
import pickle
import hashlib
import code
from typing import Any, Optional


def hash(thing):
    '''This creates a hash of a string or a binary object str=(thing)'''
    hasher=hashlib.sha256()
    if isinstance(thing,type(b'adsf')):
        hasher.update(thing)
    else:
        hasher.update(thing.encode())
    return str(hasher.hexdigest())

class sand_key(dict):
    def __init__(self, key):
        self['key'] = key
        self['key_hash']=hash(key)
        
    def sand(self,n=256):
        t_hash=list(self['key_hash'])#the key can be anything since everything has a hash
        r_list=[]
        r_list.append(str(t_hash))
        for i in range(n):
            off_set=sum(t_hash.to_bytes(),b'')%len(t_hash)
            r_list.append(hash(t_hash[off_set:]+t_hash[:off_set]))
            t_hash=list(hash(t_hash[off_set:]+t_hash[:off_set]))
        return r_list#used as the binary string key in an xor change

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
        while True:
            command = input("Enter command (GET/SET <data> or EXIT to quit): ")
            if command.upper() == "EXIT":
                break
            self['socket'].send(command.encode())
            # Receive the response
            response = self['socket'].recv(1024).decode()
            print("Response from server:", response)
        self['socket'].close()
    def get(self):
        command = "GET "
        self['socket'].send(command.encode())
        response = pickle.loads(self['socket'].recv(1024))
        print("Response from server:", response)
        return response
    def set(self, new_data):
        command = "SET ".encode()
        self['socket'].send(command)
        self['socket'].send(pickle.dumps(new_data))
        response = self['socket'].recv(1024).decode()
        print("Response from server:", response)
        return response

def _recv_until_pickle(sock: socket.socket) -> bytes:
    """Receive bytes from the socket until a full pickle payload can be loaded.

    This function keeps accumulating bytes from the socket and attempts to
    unpickle the buffer. If unpickling raises EOFError (incomplete pickle),
    it continues reading. Any other exception is raised.
    Returns the raw pickled bytes that successfully unpickle.
    """
    chunks = bytearray()
    sock.settimeout(5.0)
    while True:
        part = sock.recv(4096)
        if not part:
            # Connection closed by server; try to unpickle what we have
            try:
                pickle.loads(chunks)
                return bytes(chunks)
            except Exception as e:
                raise RuntimeError("Connection closed before receiving a complete pickle payload") from e
        chunks.extend(part)
        try:
            pickle.loads(chunks)
            return bytes(chunks)
        except EOFError:
            # Need more data
            continue
        except Exception:
            # Not a pickle yet; keep reading in case the server splits the stream
            continue


def _extract_remote_object(obj: Any) -> Any:
    """Helper to extract the server's remote object from the received object.

    The current server sends a pickled dict that contains a key 'remote' whose
    value is itself a pickled representation of the actual object. This helper
    handles both that case and the case where the server directly sends the
    object.
    """
    # Case 1: dict-like with 'remote' key containing pickled data
    try:
        if isinstance(obj, dict) and 'remote' in obj:
            maybe_bytes = obj['remote']
            if isinstance(maybe_bytes, (bytes, bytearray)):
                try:
                    return pickle.loads(maybe_bytes)
                except Exception:
                    # Fall through to return original object if nested unpickle fails
                    pass
    except Exception:
        pass
    # Default: return the object as-is
    return obj


def start_client_repl(host: str = '127.0.0.1', port: int = 65432, password: str = 'secure_password') -> Optional[Any]:
    """Connect to the server, fetch its shared object, and start a Python REPL.

    - Establishes a TCP connection and authenticates using the provided password
    - Sends a GET command to retrieve the server's shared object
    - Attempts to unpickle and extract the underlying object
    - Launches a Python interactive shell with the object bound to name `var`

    Returns the object bound to `var` for programmatic callers, or None on error.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        # Authenticate
        sock.send(password.encode())
        auth_response = sock.recv(1024).decode(errors='ignore')
        if auth_response != "SUCCESS":
            print(f"Authentication failed: {auth_response}")
            return None

        # Request the object
        sock.send(b"GET ")

        # Receive and decode the pickled payload (robust to >1024 bytes)
        raw = _recv_until_pickle(sock)
        received = pickle.loads(raw)
        remote_obj = _extract_remote_object(received)

        banner = (
            "Python REPL connected to server.\n"
            "- The server object is available as `var`.\n"
            "- Example: type(var) or print(var)\n"
            "- Press Ctrl-D (Unix) or Ctrl-Z then Enter (Windows) to exit."
        )
        # Expose minimal, helpful locals; avoid leaking socket unless needed
        local_vars = {
            'var': remote_obj,
        }
        try:
            code.interact(banner=banner, local=local_vars)
        finally:
            # Close the socket after leaving the REPL
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            sock.close()
        return remote_obj
    except Exception as e:
        try:
            sock.close()
        except Exception:
            pass
        print(f"Error starting client REPL: {e}")
        return None


if __name__ == '__main__':
    # Launch the REPL-style client by default when running this script directly
    start_client_repl()
