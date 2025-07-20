import config
from .dynamic_objects import DynamicObject


class Projectile(DynamicObject):
    """A projectile that moves with a fixed velocity.
       Optionally, it can be affected by gravity (e.g., for arrows)."""
    def __init__(self, x, y, width=10, height=10, color=(255,255,0), velocity=(10, 0), damage=config.PROJECTILE_DAMAGE, 
                 use_gravity=False, image_path=None, owner=None, animations=None):
        super().__init__(x, y, width, height, color, image_path, animations)
        self.damage = damage
        self.velocity_x, self.velocity_y = velocity
        self.use_gravity = use_gravity
        self.owner = owner  # Store the owner of the projectile (the fighter who shot it)
        # For projectiles we typically do not use the standard gravity unless needed
        if not self.use_gravity:
            self.change_y = 0  

    def update(self):
        # Move based on fixed velocity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        # Optionally apply gravity
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y