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