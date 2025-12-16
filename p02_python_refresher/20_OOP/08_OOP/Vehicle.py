from Engine import Engine

class Vehicle:

    def __init__(self, type, forSale, engine : Engine): 
        self.type = type
        self.forSale = forSale
        self.engine : Engine = engine
