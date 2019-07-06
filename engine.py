#! usr/bin/ env python3

from os import path
import pygame
import random as rn

screenWidth     = 1275
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
CYAN        = (0, 150, 255)
PURPLE      = (158,0,198)

# check bestscore from log file
scoresFiles = open(path.join(path.dirname(__file__), 'log.txt'), 'r+')
bestscore = int(scoresFiles.readline())

# initialize pygame and create a window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Bang!")
clock = pygame.time.Clock()

def scale_img(img, scale = 0.2):
    size = img.get_size()
    image = pygame.transform.scale(img, (int(size[0] * scale), int(size[1] * scale)))
    
    return image

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        all_sprites.add(self)
        mobs.add(self)

        self.gender_toss = rn.randint(0, 1)

        self.image          = mob_images[self.gender_toss][0]
        self.image          = scale_img(self.image)

        self.rect           = self.image.get_rect()
        self.rect.bottom   =  screenHeight-20 + 2
        self.radius         = int(self.rect.width * .9 / 2)
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
        toss = rn.randrange(0, 100)
        if toss == 5:
            rn.choice(zombie_sounds).play()
        if self.isDead:
            self.radius         = 1
            self.rect.bottom    = screenHeight-20 + 6
            self.image          = mob_images[self.gender_toss + 2][int(self.deadCount)]
            self.image          = scale_img(self.image)

            if self.toss:
                self.image      = pygame.transform.flip(self.image, True, False)
            self.image.set_colorkey(BLACK)

            self.deadCount += 0.5
            if self.deadCount >= 12:
                mob = Mob()
                self.kill()

        else:
            self.rect.x += self.speedx

            self.image          = mob_images[self.gender_toss][int(self.walkCount)]
            self.image.set_colorkey(BLACK)        
            self.image          = scale_img(self.image)

            if self.toss:
                self.image      = pygame.transform.flip(self.image, True, False)

            self.image.set_colorkey(BLACK)

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
        self.rect.bottom    = y - 2
        self.rect.centerx   = x

class Bullet(pygame.sprite.Sprite):
    def __init__(self, isFacing, x, y):
        pygame.sprite.Sprite.__init__(self)
        all_sprites.add(self)
        bullets.add(self)
        self.image          = pygame.Surface((30,2))
        self.image.fill(CYAN)
        self.rect           = self.image.get_rect()
        self.rect.centery   = y - 10
        self.rect.centerx   = x

        # Motion
        self.speedx = isFacing * 60

    def update(self):
        self.rect.x += self.speedx

        if self.rect.x < 0 or self.rect.x > screenWidth:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        # Initiate Sprite
        pygame.sprite.Sprite.__init__(self)

        self.image          = hero_images[0][0]
        self.image          = scale_img(self.image)
        self.image.set_colorkey(BLACK)

        self.rect           = self.image.get_rect()
        self.rect.bottom    = screenHeight-20 + 10
        self.rect.centerx   = screenWidth / 2
        self.radius         = int(self.rect.width * 0.3 / 2)

        # Motion
        self.speedx = 0

        # Status
        self.isDead     = 0
        self.deadCount  = 0

        self.isFacing   = 1         # facing Right
        
        self.isJumping  = 0
        self.jumpCount  = 0

        self.isRunning  = 0
        self.runCount   = 0

        self.bottom     = self.rect.bottom

        # Arms & Ammunition
        self.isShooting     = 0
        self.shootCount = 0
        self.ammo = 10
    
    def jump(self):
        self.rect.bottom = 1.5 * (self.jumpCount - 30) * self.jumpCount + self.bottom
        self.jumpCount += 0.5
        if self.jumpCount > 30:
            self.jumpCount = 0
            self.isJumping = 0
    
    def shoot(self):
        self.runCount = 0
        self.isShooting = 1
        pew_sound.play(loops = 0)
        bullet = Bullet(self.isFacing, self.rect.centerx, self.rect.centery)

    def update(self):
        self.isRunning = 0
        self.speedx = 0

        if self.isDead:
            self.rect.bottom    = screenHeight-20 + 10
            self.image          = hero_images[3][int(self.deadCount)]
            
            self.image          = scale_img(self.image)

            if self.isFacing == -1:
                self.image  = pygame.transform.flip(self.image, True, False)
            
            self.image.set_colorkey(BLACK)

            self.deadCount += 0.5
            if self.deadCount > 14:
                self.isDead = 2
                self.deadCount = 0

        else:
            # Process Key Press
            key_state = pygame.key.get_pressed()
            if key_state[pygame.K_RIGHT]:
                self.isRunning  = 1
                self.speedx     = 5
                self.isFacing   = 1
            if key_state[pygame.K_LEFT]:
                self.isRunning  = 1
                self.speedx     = -5
                self.isFacing   = -1
            if key_state[pygame.K_UP]:
                self.isJumping  = 1
            
            if self.isFacing == -1:
                self.radius     = 0
            else:
                self.radius     = int(self.rect.width * 0.3 / 2)

            # Update Motion
            if self.isShooting:
                self.image = hero_images[1][int(self.shootCount)]
                self.shootCount += 0.5
                if self.shootCount == 6:
                    self.shootCount = 0
                    self.isShooting = 0
            elif self.isRunning:
                self.image      = hero_images[0][int(self.runCount)]
                self.runCount   += 0.5
                if self.runCount == 13:
                    self.runCount = 0
            else:
                self.image = hero_images[1][0]

            if self.isJumping:
                self.image = hero_images[2][int(self.jumpCount)]

            self.image          = scale_img(self.image)

            if self.isFacing == -1:
                self.image  = pygame.transform.flip(self.image, True, False)
            
            self.image.set_colorkey(BLACK)

            if self.isJumping:
                self.jump()
            self.rect.x += self.speedx

            # Boundary Conditions
            if self.rect.right > screenWidth:
                self.rect.right = screenWidth
            if self.rect.left < 0:
                self.rect.left  = 0

# import images
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

hero_dead = [pygame.image.load(path.join(hero_sprites, 'Death', 'Death_000.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_001.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_002.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_003.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_004.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_005.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_006.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_007.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_008.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_009.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_010.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_011.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_012.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_013.png')).convert(),
             pygame.image.load(path.join(hero_sprites, 'Death', 'Death_014.png')).convert()]

bg = pygame.image.load(path.join(img, 'backGround', 'bg.png'))
bg = scale_img(bg, scale=2)

mob_images = [male_walk_img, female_walk_img, male_dead_img, female_dead_img]
hero_images = [hero_run, hero_shoot, hero_jump, hero_dead]

# import sounds
snd = path.join(path.dirname(__file__), 'snd')
zombie_sounds = []
for sound in ['Zombie Attack Sound.wav', 'Zombie Sound.wav', 'Zombie Sound 2.wav']:
    zombie_sounds.append(pygame.mixer.Sound(path.join(snd, sound)))
for sound in zombie_sounds:
    sound.set_volume(0.01)

pew_sound = pygame.mixer.Sound(path.join(snd, 'laser1.wav'))
pew_sound.set_volume(0.05)
death_sound = pygame.mixer.Sound(path.join(snd, 'death.ogg'))
death_sound.set_volume(0.1)
pygame.mixer.music.load(path.join(snd, 'aosi - doom.wav'))
pygame.mixer.music.set_volume(10)

# define text
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)

    surf.blit(text_surface, text_rect)

# define Gameover Screen
def showGameOverScreen():
    waiting = True

    while waiting:
        clock.tick(FPS)
        screen.blit(bg, (0,0))
        draw_text(screen, 'Best Score: ' + str(bestscore) + '    Last Score: ' + str(score), 30, screenWidth / 2, 30)
        draw_text(screen, 'BANG!', 256, screenWidth / 2, screenHeight / 4)
        draw_text(screen, 'ARROW Keys for movement , SPACE Key for shooting', 40, screenWidth / 2, screenHeight - 200)
        draw_text(screen, 'Press ENTER key to start', 20, screenWidth / 2, screenHeight - 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    running = True
        
        pygame.display.flip()
    
    return running

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
ammo = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

kills = 0
wavechange = 0

# Game loop
pygame.mixer.music.play(loops = -1)

score = 0
gameover = True
running = True
while running:

    if gameover:
        all_sprites.empty()
        bullets.empty()
        mobs.empty()
        ammo.empty()

        running = showGameOverScreen()

        player = Player()
        all_sprites.add(player)

        for i in range(3):
            m = Mob()

        kills = 0
        score = 0
        gameover = False

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
        if hit.isDead == False:
            # Increase Score
            kills += 1
            score += 2 + int(abs(hit.speedx))
            # Initiate Die Sequence
            hit.isDead = True
            # Drop Ammo
            R = rn.randrange(3)
            for i in range(R):
                bullet = Ammo(hit.rect.x, hit.rect.bottom)
            print('Kills: ', kills)

     # Check collision b/w player and ammo
    hits = pygame.sprite.spritecollide(player, ammo, True)
    for hit in hits:
        player.ammo += 1
    
     # Check wether player has squashed mob
    for m in mobs:
        if abs(player.rect.bottom - m.rect.top) <= 40 and abs(player.rect.centerx - m.rect.centerx) <= 40:
            mobs.remove(m)
            kills += 1
            score += 2 + int(abs(m.speedx))
            # Initiate Die Sequence
            m.isDead = True
            # Drop Ammo
            R = rn.randrange(3)
            for i in range(R):
                bullet = Ammo(m.rect.x, m.rect.bottom)
            print('Kills: ', kills)

     # Check collision b/w mobs and player
    hits = pygame.sprite.spritecollide(player, mobs, False, collided= pygame.sprite.collide_circle)
    if hits:
        death_sound.play()
        player.isDead = 1
        for hit in hits:
            hit.speedx = 0

    all_sprites.update()
    
    text = 'Score: ' + str(score) + '   Ammo: ' + str(player.ammo)

     # spawn extra mob for every 40 kills
    for i in range(int(kills / 40)):
        wavechange = 1
        m = Mob()
        kills = 0

    # draw
    screen.blit(bg, (0,0))
    ground = pygame.rect.Rect(0,screenHeight-20, screenWidth, 25)
    pygame.draw.rect(screen, BLACK, ground)
    all_sprites.draw(screen)
    draw_text(screen, text, 50, screenWidth / 2, 30)

    if wavechange:
        draw_text(screen, 'More Mobs Added', 64, screenWidth / 2, screenHeight / 2 - 100)
        wavechange += 1
        wavechange %= 60

    # flip display
    pygame.display.flip()

    if player.isDead == 2:
        gameover = True
        bestscore = max(bestscore, score)
        # scoresFiles.write('\n')
        scoresFiles.seek(0)
        scoresFiles.write(str(bestscore))
        print('\nScore: ', score, 'Kills: ', kills)
        print('GameOver')


scoresFiles.close()
pygame.quit()