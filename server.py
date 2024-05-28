import socketserver
import os

DATABASE_FILE = 'data.txt'

database = {}

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
        if not database:
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r') as f:
                    for line in f:
                        record = line.strip().split('|')
                        if len(record) != 4:
                            print(f"Record skipped [missing field(s)]: {line}")
                        elif self.is_valid_record(record, line):
                            name = record[0].lower()
                            database[name] = record
            print("Python DB server is now running...")

    def is_valid_record(self, record, line):
        if not record[0].isalpha():
            print(f"Record skipped [invalid name]: {line}")
            return False
        if len(record) > 1 and record[1]:
            try:
                age = int(record[1])
                if age < 1 or age > 120:
                    print(f"Record skipped [invalid age field]: {line}")
                    return False
            except ValueError:
                print(f"Record skipped [invalid age field]: {line}")
                return False
        if len(record) > 2 and record[2]:
            if not all(c.isalnum() or c in " .-" for c in record[2]):
                print(f"Record skipped [invalid address field]: {line}")
                return False
        if len(record) > 3 and record[3]:
            if not ([i.isnumeric() for i in record[3]].count(True) in [7,10] and record[3][-5] == '-'):
                print(f"Record skipped [invalid phone field]: {line}")
                return False
            if len(record[3]) == 10 and record[3][3] != " ":
                print(f"Record skipped [invalid phone field]: {line}")
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

    def write_to_file(self):
        with open(DATABASE_FILE, "w") as f:
            for i, j in database.items():
                f.write("|".join(j))
                f.write("\n")
            f.close()

    def find_customer(self, name):
        name = name.lower()
        return '|'.join(database.get(name, ["Customer not found"]))

    def add_customer(self, params):
        name = params[0].lower()
        if name in database:
            return "Customer already exists"
        if not self.is_valid_record(params, line="|".join(params)):
            return "Invalid customer data"
        database[name] = params
        #self.write_to_file()
        return "Customer added"

    def delete_customer(self, name):
        name = name.lower()
        if name not in database:
            return "Customer does not exist"
        del database[name]
        #self.write_to_file()
        return "Customer deleted"

    def update_customer(self, name, field, value):
        name = name.lower()
        print(name, field, value)
        if name not in database:
            return "Customer not found"
        index = {'age': 1, 'address': 2, 'phone': 3}[field]
        if field == "age" and (value <= 1 or value >= 120):
            return "Invalid age. Age should be between 1 and 120. Try again"
        elif field == "phone" and not ([i.isnumeric() for i in value].count(True) in [7,10] and value[-5] == '-'):
            return "Invalid phone number. Try again"
        database[name][index] = value
        #self.write_to_file()
        return "Customer updated"

    def print_report(self):
        print(len(database))
        report = "\n".join('|'.join(record) for record in sorted(database.values()))
        return report

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.TCPServer((HOST, PORT), DatabaseServerHandler) as server:
        print("Server started at {}:{}".format(HOST, PORT))
        server.serve_forever()

