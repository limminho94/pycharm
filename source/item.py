class Item:
    def __init__(self, item_name, item_weight, item_image):
        self.name = item_name
        self.weight = item_weight
        self.image = item_image

    def get_name(self):
        return  self.name

    def get_weight(self):
        return self.weight

    def show_image(self):
        print(self.image)


class WearableItem(Item):
    def __init__(self, item_name, item_weight, item_image, item_location, item_state):
        super().__init__(item_name, item_weight, item_image)
        self.location = item_location
        self.state = item_state

    def get_name(self):
        return "장비:"+ self.name

    def get_location(self):
        return self.location

    def get_state(self):
        return self.state


# weapon_1 = WearableItem(item_name="sword", item_weight=5, item_image="sword.jpg", item_location="양손", item_state=False)
# weapon_2 = WearableItem(item_name="bow", item_weight=3, item_image="bow.jpg", item_location="양손", item_state=False)
# print(weapon_1.get_weight())


class WeaponItem(WearableItem):
    def __init__(self, item_name, item_weight, item_image, item_location, item_state, item_attack_damage, item_attack_speed):
        super().__init__(item_name, item_weight, item_image, item_location, item_state)
        self.attack_damage = item_attack_damage
        self.attack_speed = item_attack_speed

    def attack(self):
        return self.attack_damage * self.attack_speed

weapon_1 = WeaponItem(item_name="sword", item_weight=5, item_image="sword.jpg", item_location="양손", item_state=False, item_attack_damage=10 ,item_attack_speed=1)
weapon_2 = WeaponItem(item_name="bow", item_weight=3, item_image="bow.jpg", item_location="양손", item_state=False, item_attack_damage=10, item_attack_speed=0.5)


class MeleeWeapon(WeaponItem): pass


class RangeWeapon(WeaponItem):
    def __init__(self, item_name, item_weight, item_image, item_location, item_state, item_attack_damage, item_attack_speed, item_range_length):
        super().__init__(item_name, item_weight, item_image, item_location, item_state, item_attack_damage, item_attack_speed)
        self.range_length = item_range_length





