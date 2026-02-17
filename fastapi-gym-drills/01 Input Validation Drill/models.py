# models.py

class Package:
    def __init__(self, weight: float, destination: str, tags: set[str]):
        self.weight = weight
        self.destination = destination
        self.tags = tags
