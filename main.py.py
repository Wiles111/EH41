# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 11:28:24 2025

@author: derek
"""

from client import Client
from service import Service
from appointment import Appointment
from business import BeautyBusiness
from datetime import datetime

# Initialize the business manager
business = BeautyBusiness("EH41")

# Sample services (can be extended)
business.add_service(Service("Eyebrow Tattoo", 250, 90, "Brows"))
business.add_service(Service("Lip Filler", 400, 60, "Lips"))
business.add_service(Service("Eyelash Extensions", 120, 75, "Lashes"))

# Simple menu loop
def main_menu():
    while True:
        print("\nWelcome to", business.name)
        print("1. Add Client")
        print("2. Book Appointment")
        print("3. View Appointments")
        print("4. View Clients")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Client Name: ")
            phone = input("Phone Number: ")
            email = input("Email: ")
            business.add_client(Client(name, phone, email))

        elif choice == "2":
            client_name = input("Client Name: ")
            service_name = input("Service Name: ")
            date_str = input("Date (YYYY-MM-DD): ")
            time_str = input("Time (HH:MM): ")
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            business.book_appointment(client_name, service_name, dt)

        elif choice == "3":
            business.list_appointments()

        elif choice == "4":
            business.list_clients()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main_menu()
