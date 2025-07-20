from .dynamic_objects import DynamicObject


class PowerUp(DynamicObject):
    """A power-up that moves with a fixed velocity.
       Optionally, it can be affected by gravity."""
    def __init__(self, x, y, type, amount, width=10, height=10, color=(255,255,0), animations=None):
        super().__init__(x, y, width, height, color, animations)
        self.upgrade_type = type
        self.amount = amount
        self.duration = 10
        self.use_gravity = False
        
    def update(self):
        # Optionally apply gravity
        if self.use_gravity:
            self.calc_grav()
            self.rect.y += self.change_y
