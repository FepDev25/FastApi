from Enemy import Enemy

zombie = Enemy()
zombie.type_of_enemy = 'Zombie'
print(f'{zombie.type_of_enemy} has {zombie.health_points} health points and can do attack of {zombie.attack_damage}')

zombie.talk()
zombie.walk_foreward()
zombie.attack()