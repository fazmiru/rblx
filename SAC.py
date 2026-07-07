class Character:
    def __init__(self, strName, intHealth):
        self.name = strName
        self.health = intHealth

    def take_damage(self, intAmount):
        self.health -= intAmount
        if self.health < 0:
            self.health = 0
            return "Entity Destroyed!"

    def is_alive(self):
        return self.health > 0


class Survivor(Character):
    def __init__(self, strName, intHealth, intAmmo):
        super().__init__(strName, intHealth)
        self.ammo = intAmmo

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return "Bang!"
        else:
            return "Out of ammo!"


class Zombie(Character):
    def __init__(self, strName, intHealth, intBiteDamage):
        super().__init__(strName, intHealth)
        self.intBiteDamage = intBiteDamage

    def bite(self):
        return f"Chomp! deals {self.intBiteDamage} damage!"

# Example usage
survivor1 = Survivor("Leon", 100, 10)
zombie1 = Zombie("Walker", 50, 100)
