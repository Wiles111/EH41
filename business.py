import json
from appointment import Appointment
from client import Client
from service import Service
from datetime import datetime

class BeautyBusiness:
    def __init__(self, name):
        self.name = name
        self.clients = []
        self.services = []
        self.appointments = []
        self.load_data()

    def add_client(self, client):
        self.clients.append(client)
        print(f"Added client: {client.name}")
        self.save_data()

    def add_service(self, service):
        self.services.append(service)

    def find_client(self, name):
        for client in self.clients:
            if client.name.lower() == name.lower():
                return client
        return None

    def find_service(self, name):
        for service in self.services:
            if service.name.lower() == name.lower():
                return service
        return None

    def book_appointment(self, client_name, service_name, dt):
        client = self.find_client(client_name)
        service = self.find_service(service_name)
        if client and service:
            appt = Appointment(client, service, dt)
            self.appointments.append(appt)
            client.history.append(appt)
            print("Appointment booked!")
            self.save_data()
        else:
            print("Client or Service not found.")

    def list_appointments(self):
        for appt in self.appointments:
            print(appt)

    def list_clients(self):
        for client in self.clients:
            print(client)

    def save_data(self):
        data = {
            "clients": [
                {"name": c.name, "phone": c.phone, "email": c.email}
                for c in self.clients
            ],
            "appointments": [
                {
                    "client": a.client.name,
                    "service": a.service.name,
                    "datetime": a.datetime.strftime("%Y-%m-%d %H:%M")
                }
                for a in self.appointments
            ]
        }
        with open("beauty_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open("beauty_data.json", "r") as f:
                data = json.load(f)
                for c in data["clients"]:
                    client = Client(c["name"], c["phone"], c["email"])
                    self.clients.append(client)

                for a in data["appointments"]:
                    client = self.find_client(a["client"])
                    service = self.find_service(a["service"])
                    if client and service:
                        dt = datetime.strptime(a["datetime"], "%Y-%m-%d %H:%M")
                        appt = Appointment(client, service, dt)
                        self.appointments.append(appt)
                        client.history.append(appt)
        except FileNotFoundError:
            pass


