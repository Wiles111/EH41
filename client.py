class Client:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email
        self.history = []

    def __str__(self):
        return f"{self.name} | {self.phone} | {self.email}"
