class Appointment:
    def __init__(self, client, service, datetime):
        self.client = client
        self.service = service
        self.datetime = datetime
        self.status = "Booked"

    def __str__(self):
        return f"{self.datetime.strftime('%Y-%m-%d %H:%M')} - {self.client.name} - {self.service.name}"
