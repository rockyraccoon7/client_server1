import socketserver
import os

DATABASE_FILE = 'data.txt'

class DatabaseServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.load_database()
        while True:
            self.data = self.request.recv(1024).strip().decode('utf-8')
            if not self.data:
                break
            command, *params = self.data.split('|')
            response = self.handle_command(command, params)
            self.request.sendall(response.encode('utf-8'))

    def load_database(self):
        self.database = {}
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r') as f:
                for line in f:
                    record = line.strip().split('|')
                    if self.is_valid_record(record):
                        name = record[0].lower()
                        self.database[name] = record
                    else:
                        print(f"Invalid record ignored: {line.strip()}")

    def is_valid_record(self, record):
        if not record[0].isalpha():
            print("Invalid name")
            return False
        if len(record) > 1 and record[1]:
            try:
                age = int(record[1])
                if age < 1 or age > 120:
                    print("Invalid age 1")
                    return False
            except ValueError:
                print("Invalid age 2")
                return False
        if len(record) > 2 and record[2]:
            if not all(c.isalnum() or c in " .-" for c in record[2]):
                print("Invalid address")
                return False
        if len(record) > 3 and record[3]:
            if not ([i.isnumeric() for i in record[3]].count(True) in [7,10] and record[3][-5] == '-'):
                print("Invalid phone number")
                return False
            if len(record[3]) == 10 and record[3][3] != " ":
                print("Invalid phone number 2")
                return False
        return True

    def handle_command(self, command, params):
        if command == "find":
            return self.find_customer(params[0])
        elif command == "add":
            return self.add_customer(params)
        elif command == "delete":
            return self.delete_customer(params[0])
        elif command == "update_age":
            return self.update_customer(params[0], 'age', params[1])
        elif command == "update_address":
            return self.update_customer(params[0], 'address', params[1])
        elif command == "update_phone":
            return self.update_customer(params[0], 'phone', params[1])
        elif command == "report":
            return self.print_report()
        return "Invalid command"

    def find_customer(self, name):
        name = name.lower()
        return '|'.join(self.database.get(name, ["Customer not found"]))

    def add_customer(self, params):
        name = params[0].lower()
        if name in self.database:
            return "Customer already exists"
        if not self.is_valid_record(params):
            return "Invalid customer data"
        self.database[name] = params
        return "Customer added"

    def delete_customer(self, name):
        name = name.lower()
        if name not in self.database:
            return "Customer does not exist"
        del self.database[name]
        return "Customer deleted"

    def update_customer(self, name, field, value):
        name = name.lower()
        if name not in self.database:
            return "Customer not found"
        index = {'age': 1, 'address': 2, 'phone': 3}[field]
        self.database[name][index] = value
        return "Customer updated"

    def print_report(self):
        report = "\n".join('|'.join(record) for record in sorted(self.database.values()))
        return report

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.TCPServer((HOST, PORT), DatabaseServerHandler) as server:
        print("Server started at {}:{}".format(HOST, PORT))
        server.serve_forever()

