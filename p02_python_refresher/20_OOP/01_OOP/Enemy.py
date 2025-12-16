class Enemy:
    type_of_enemy: str
    health_points: int = 10
    attack_damage: int = 1

    def talk(self):
        print(f"Hola soy in {self.type_of_enemy}. Preparado para pelear")
    
    def walk_foreward(self):
        print(f"{self.type_of_enemy} se mueve cerca de ti.")

    def attack(self):
        print(f"{self.type_of_enemy} ataca con {self.attack_damage} de daño")