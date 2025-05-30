# my h & g keys are broken so I put them here
import pygame  # Import pygame for game functionality
import config  # Import configuration settings like scene dimensions and FPS

# Import platform and dynamic object classes from the new files
from src.engine.platforms import *
from src.engine.dynamic_objects import *

pygame.init()  # Initialize all imported pygame modules

# Set up the main game window using dimensions from config
scene = pygame.display.set_mode((config.SCENE_WIDTH, config.SCENE_HEIGHT)) 

# Load a background image located in the assets folder
background = pygame.image.load("src/assets/images/country-platform-preview.png")
background = pygame.transform.scale(background, (config.SCENE_WIDTH, config.SCENE_HEIGHT))

# Set the window title using the caption defined in config
pygame.display.set_caption(config.CAPTION)

# Create a clock to manage the game's frame rate
clock = pygame.time.Clock()

# Create sprite groups to better organize and manage game objects.
all_sprites = pygame.sprite.Group()      # Contains all objects for global update and drawing
platforms = pygame.sprite.Group()          # Contains all platform objects
enemies = pygame.sprite.Group()            # Contains all enemy objects
projectiles = pygame.sprite.Group()        # Contains all projectile objects
fighters = pygame.sprite.Group()        # Contains all fighter objects

# Create game objects with specified positions, sizes, and behaviors
static_platform = Platform(config.SCENE_WIDTH/4, config.SCENE_HEIGHT*3/5, 
                           500,100, 
                           color=(139,69,19))
static_platform2 = Platform(config.SCENE_WIDTH/4 + 450, config.SCENE_HEIGHT*3/5 - 50, 
                           50,50, 
                           color=(139,69,19))
static_platform3 = Platform(0, config.SCENE_HEIGHT - 20, 
                           1200,20, 
                           color=(139,69,19))
# MovingPlatform moves horizontally within a given range and speed
moving_platform = MovingPlatform(config.SCENE_WIDTH/8, config.SCENE_HEIGHT/4,
                                 config.SCENE_WIDTH/4, 10, range_x=150, range_y=0, speed=1)
# Two fighter objects using custom control keys for movement, jumping, and shooting.
fighter1 = Fighter(450,  
            static_platform.rect.y - 70, color=(0, 0, 255), 
                   controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "shoot": pygame.K_SPACE},
                   image_path="src/assets/images/fighter.png")
print(fighter1.rect.top)
print(fighter1.rect.bottom)
fighter2 = Fighter(650, 450, color=(255, 255, 0), 
                   controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP})
# An enemy that patrols horizontally and bounces at screen edges
enemy = NPC(static_platform.rect.x + (static_platform.rect.width / 2) - (30 / 2),  
            static_platform.rect.y - 30, 
            speed=config.NPC_SPEED, image_path="src/assets/images/death-lamp-walk6.png")

# Add each object to the appropriate sprite groups for updating and drawing
all_sprites.add(static_platform,static_platform2, moving_platform, fighter1, fighter2, enemy, static_platform3)
platforms.add(static_platform, static_platform2, moving_platform, static_platform3)
enemies.add(enemy)
fighters.add(fighter1, fighter2)

running = True
while running:
    # Process input events (such as closing the window or shooting projectiles)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # If the shoot key for fighter1 is pressed, spawn a projectile.
            if event.key == fighter1.controls.get("shoot"):
                projectile = fighter1.shoot()
                all_sprites.add(projectile)
                projectiles.add(projectile)
    # Update all game objects (calls update() on each sprite in all_sprites)
    all_sprites.update()

    # Handle collisions so dynamic objects can stand on platforms.
    for sprite in all_sprites:
        if isinstance(sprite, DynamicObject):
            sprite.handle_platform_collision(platforms)
        if isinstance(sprite, Projectile):
            # Check for collisions with enemies and remove the projectile if it hits
            hit_enemies = pygame.sprite.spritecollide(sprite, enemies, False)
            if hit_enemies:
                for enemy in hit_enemies:
                    enemy.take_damage(sprite.damage)
                    sprite.kill()
            # Check for collisions with fighters, but not with the projectile's owner
            hit_fighters = pygame.sprite.spritecollide(sprite, fighters, False)
            for fighter in hit_fighters:
                if fighter != sprite.owner:  # Prevent projectile from damaging its owner
                    fighter.take_damage(sprite.damage)
                    sprite.kill()
            hit_platforms = pygame.sprite.spritecollide(sprite,platforms, False)
            for platform in hit_platforms:
                sprite.kill()
               
    
    # Draw phase: clear the screen, draw background, and then all sprites
    scene.fill((0, 0, 0))
    scene.blit(background, (0, 0))
    all_sprites.draw(scene)
    for sprite in all_sprites:
        if isinstance(sprite, Player):  #NFC and Fither
            sprite.draw_health_bar(scene)
    pygame.display.flip()  # Refresh the ng = Falsedisplay
    clock.tick(config.FPS)  # Maintain the FPS defined in config

pygame.quit()  # Clean up and close the pygame window
