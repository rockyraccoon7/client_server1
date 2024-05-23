import socket
import os

def clear_screen():
    os.system('clear')

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 9999))
        sock.sendall(request.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        return response

def main():
    while True:
        clear_screen()
        print("Customer Management Menu")
        print("1. Find customer")
        print("2. Add customer")
        print("3. Delete customer")
        print("4. Update customer age")
        print("5. Update customer address")
        print("6. Update customer phone")
        print("7. Print report")
        print("8. Exit")
        choice = input("Select: ")

        if choice == '1':
            name = input("Enter customer name: ")
            request = f"find|{name}"
        elif choice == '2':
            first_name = input("First name: ")
            age = input("Age: ")
            address = input("Address: ")
            phone = input("Phone: ")
            request = f"add|{first_name}|{age}|{address}|{phone}"
        elif choice == '3':
            name = input("Enter customer name: ")
            request = f"delete|{name}"
        elif choice == '4':
            name = input("Enter customer name: ")
            age = input("Enter new age: ")
            request = f"update_age|{name}|{age}"
        elif choice == '5':
            name = input("Enter customer name: ")
            address = input("Enter new address: ")
            request = f"update_address|{name}|{address}"
        elif choice == '6':
            name = input("Enter customer name: ")
            phone = input("Enter new phone: ")
            request = f"update_phone|{name}|{phone}"
        elif choice == '7':
            request = "report|"
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        response = send_request(request)
        print("Server response:", response)
        input("Press any key to continue...")

if __name__ == "__main__":
    main()
