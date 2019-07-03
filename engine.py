#! usr/bin/ env python3

from os import path
import pygame
import random as rn

screenWidth     = 1280
screenHeight    = 800
FPS             = 60

# define colours
NAVYBLUE    = (10, 20, 255)
BLUE        = (0, 0, 255)
RED         = (255, 0, 0)
YELLOW      = (255, 255, 0)
GREEN       = (0, 255, 0)
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
CYAN        = (0, 255, 255)
PURPLE      = (158,0,198)



class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        all_sprites.add(self)
        mobs.add(self)

        self.gender_toss = rn.randint(0, 1)

        self.image          = mob_images[self.gender_toss][0]
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0] / 5), int(self.size[1] / 5)))

        self.rect           = self.image.get_rect()
        self.rect.bottom   = 0.75 * screenHeight + 2
        self.radius         = int(self.rect.width * .9 / 2)
        pygame.draw.circle(self.image, WHITE, self.rect.center, self.radius)
        self.walkCount      = 0

        x1 = rn.randrange(-50, 0)
        x2 = rn.randrange(screenWidth, screenWidth + 50)
        self.toss = rn.randint(0, 1)
        if self.toss:
            self.rect.centerx = x2
        else:
            self.rect.centerx = x1

        # Motion
        if self.toss:
            self.image = pygame.transform.flip(self.image, True, False)
            self.speedx = -0.5 * rn.randrange(2, 10)
        else:
            self.speedx = 0.5 * rn.randrange(2, 10)

        self.isDead = False
        self.deadCount = 0

    def update(self):
        if self.isDead:
            mobs.remove(self)
            self.rect.bottom   = 0.75 * screenHeight + 6
            self.image          = mob_images[self.gender_toss + 2][int(self.deadCount)]
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (int(self.size[0] / 5), int(self.size[1] / 5)))
            if self.toss:
                self.image = pygame.transform.flip(self.image, True, False)
            self.image.set_colorkey(BLACK)

            self.deadCount += 0.5
            if self.deadCount >= 12:
                mob = Mob()
                self.kill()

        else:
            self.rect.x += self.speedx

            self.image          = mob_images[self.gender_toss][int(self.walkCount)]
            self.image.set_colorkey(BLACK)        
            self.size = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (int(self.size[0] / 5), int(self.size[1] / 5)))
            if self.toss:
                self.image = pygame.transform.flip(self.image, True, False)

            self.image.set_colorkey(BLACK)
            pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

            self.walkCount      += 0.25 * abs(self.speedx)
            if self.walkCount > 9:
                self.walkCount = 0

            if self.rect.left > screenWidth + 50 or self.rect.right < -50:
                self.kill()
                
                mob = Mob()

class Ammo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        all_sprites.add(self)
        ammo.add(self)
        self.image          = pygame.Surface((10,5))
        self.image.fill(RED)
        self.rect           = self.image.get_rect()
        self.rect.bottom    = y
        self.rect.centerx   = x

class Bullet(pygame.sprite.Sprite):
    def __init__(self, isFacing, x, y):
        pygame.sprite.Sprite.__init__(self)
        all_sprites.add(self)
        bullets.add(self)
        self.image          = pygame.Surface((20,2))
        self.image.fill(CYAN)
        self.rect           = self.image.get_rect()
        self.rect.centery   = y - 10
        self.rect.centerx   = x

        # Motion
        self.speedx = isFacing * 15

    def update(self):
        self.rect.x += self.speedx

        if self.rect.x < 0 or self.rect.x > screenWidth:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.isShooting     = 0

        self.image          = hero_images[self.isShooting][0]
        self.image.set_colorkey(BLACK)
        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0] / 5), int(self.size[1] / 5)))

        self.rect           = self.image.get_rect()
        self.rect.bottom    = 0.75 * screenHeight + 10
        self.rect.centerx   = screenWidth / 2
        self.radius         = int(self.rect.width * 0.3 / 2)

        # Motion
        self.speedx = 0
        self.bottom = self.rect.bottom

        # Orientation
        self.isFacing   = 1         # facing Right
        self.isJumping  = 0
        self.isRunning  = 0
        self.jumpCount  = 0
        self.runCount   = 0
        self.shootCount = 0

        if self.isFacing == -1:
            self.radius = 0
        else:
            self.radius = int(self.rect.width * 0.3 / 2)
        # Arms & Ammunition
        self.ammo = 15
    
    def jump(self):
        self.rect.bottom = 1.5 * (self.jumpCount - 30) * self.jumpCount + self.bottom
        self.jumpCount += 0.5
        if self.jumpCount > 30:
            self.jumpCount = 0
            self.isJumping = 0
    
    def shoot(self):
        self.runCount = 0
        self.isShooting = 1
        bullet = Bullet(self.isFacing, self.rect.centerx, self.rect.centery)

    def update(self):
        self.isRunning = 0
        self.speedx = 0

        # Process Key Press
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_RIGHT]:
            self.isRunning = 1
            self.speedx = 5
            self.isFacing = 1
        if key_state[pygame.K_LEFT]:
            self.isRunning = 1
            self.speedx = -5
            self.isFacing = -1
        if key_state[pygame.K_UP]:
            self.isJumping = 1
        
        if self.isFacing == -1:
            self.radius = 0
        else:
            self.radius = int(self.rect.width * 0.3 / 2)

        # Update Motion
        if self.isShooting:
            self.image = hero_images[1][int(self.shootCount)]
            self.shootCount += 0.5
            if self.shootCount == 6:
                self.shootCount = 0
                self.isShooting = 0
        elif self.isRunning:
            self.image = hero_images[0][int(self.runCount)]
            self.runCount += 0.5
            if self.runCount == 13:
                self.runCount = 0
        else:
            self.image = hero_images[1][0]

        if self.isJumping:
            self.image = hero_images[2][int(self.jumpCount)]

        self.size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(self.size[0] / 5), int(self.size[1] / 5)))

        if self.isFacing == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.image.set_colorkey(BLACK)

        if self.isJumping:
            self.jump()
        self.rect.x += self.speedx

        # Boundary Conditions
        if self.rect.right > screenWidth:
            self.rect.right = screenWidth
        if self.rect.left < 0:
            self.rect.left = 0

# initialize pygame and create a window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Bang!")
clock = pygame.time.Clock()

# define images
img = path.join(path.dirname(__file__), 'img')
female_sprites = path.join(img, 'female')
male_sprites = path.join(img, 'male')
hero_sprites = path.join(img, 'The Hero', 'Animations')
male_walk_img = [pygame.image.load(path.join(male_sprites, 'Walk (1).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (2).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (3).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (4).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (5).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (6).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (7).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (8).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (9).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Walk (10).png')).convert()]

male_dead_img = [pygame.image.load(path.join(male_sprites, 'Dead (1).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (2).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (3).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (4).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (5).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (6).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (7).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (8).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (9).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (10).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (11).png')).convert(),
                 pygame.image.load(path.join(male_sprites, 'Dead (12).png')).convert()]

female_walk_img = [pygame.image.load(path.join(female_sprites, 'Walk (1).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (2).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (3).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (4).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (5).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (6).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (7).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (8).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (9).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Walk (10).png')).convert()]

female_dead_img = [pygame.image.load(path.join(female_sprites, 'Dead (1).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (2).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (3).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (4).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (5).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (6).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (7).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (8).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (9).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (10).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (11).png')).convert(),
                   pygame.image.load(path.join(female_sprites, 'Dead (12).png')).convert()]

hero_run = [pygame.image.load(path.join(hero_sprites, 'Run', 'Run_000.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_001.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_002.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_003.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_004.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_005.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_006.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_007.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_008.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_009.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_010.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_011.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_012.png')).convert(),
            pygame.image.load(path.join(hero_sprites, 'Run', 'Run_013.png')).convert()]

hero_shoot = [pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_000.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_001.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_003.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_004.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_011.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_014.png')).convert(),
              pygame.image.load(path.join(hero_sprites, 'Shoot', 'Shoot_000.png')).convert()]

hero_jump = [pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_000.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_001.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_004.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_006.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_007.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_008.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_000.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_001.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_002.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_002.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_003.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_003.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_004.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_004.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_005.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_005.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_006.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_006.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_007.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_008.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_008.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_009.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_009.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_010.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jetpack Fly Forward', 'Jetpack Fly Forward_011.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_008.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_007.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_006.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_004.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_001.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Jump Start', 'Jump Start_008.png')).convert()]


mob_images = [male_walk_img, female_walk_img, male_dead_img, female_dead_img]
hero_images = [hero_run, hero_shoot, hero_jump]

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
ammo = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(5):
    m = Mob()

# Game loop
score = 0
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    
    # process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if player.ammo:             # Check if ammo is available
                    player.shoot()
                    player.ammo -= 1
    
    # update
     # Check collision b/w mobs and bullets
    hits = pygame.sprite.groupcollide(mobs, bullets, False, True)
    for hit in hits:
        print('Score: ', score,', Ammo: ', player.ammo)
        # Increase Score
        score += 2
        # Initiate Die Sequence
        hit.isDead = True
        # Drop Ammo
        R = rn.randrange(3)
        for i in range(R):
            bullet = Ammo(hit.rect.x, hit.rect.bottom - 2) 

     # Check collision b/w player and ammo
    hits = pygame.sprite.spritecollide(player, ammo, True)
    for hit in hits:
        player.ammo += 1
        print('Score: ', score,', Ammo: ', player.ammo)

     # Check collision b/w mobs and player
    hits = pygame.sprite.spritecollide(player, mobs, False, collided= pygame.sprite.collide_circle)
    if hits or score >= 150:
        running = False
        print('GAMEOVER')

    all_sprites.update()
    
    # draw
    screen.fill(BLACK)
    ground = pygame.Rect(0, screenHeight * 0.75, screenWidth, screenHeight * 0.25)
    pygame.draw.rect(screen, PURPLE, ground)
    all_sprites.draw(screen)

    # flip display
    pygame.display.flip()

print('Score: ', score,', Ammo: ', player.ammo)
pygame.quit()