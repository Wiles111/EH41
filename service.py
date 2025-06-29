class Service:
    def __init__(self, name, price, duration, category):
        self.name = name
        self.price = price
        self.duration = duration  # in minutes
        self.category = category

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.duration} mins)"
