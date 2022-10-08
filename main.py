import pygame
import random

# Inicializace hry
pygame.init()

# Obrazovku
width = 1200
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bitva s mozkomory")

# Nastavení hry
fps = 60
clock = pygame.time.Clock()


# Classy
class Game:
    def __init__(self, our_player, group_of_mozkomors):
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.slow_down_cycle = 0

        self.our_player = our_player
        self.group_of_mozkomors = group_of_mozkomors

        # Hudba v pozadí
        pygame.mixer.music.load("media/bg-music-hp.wav")
        pygame.mixer.music.play(-1, 0.0)

        # Fonty
        self.potter_font = pygame.font.Font("fonts/Harry.ttf", 24)
        self.potter_font_big = pygame.font.Font("fonts/Harry.ttf", 45)

        # Obrázek v pozadí
        self.background_image = pygame.image.load("img/bg-dementors.png")
        self.background_image_rect = self.background_image.get_rect()
        self.background_image_rect.topleft = (0, 0)

        # Obrázky
        blue_image = pygame.image.load("img/mozkomor-modry.png")
        green_image = pygame.image.load("img/mozkomor-zeleny.png")
        purple_image = pygame.image.load("img/mozkomor-ruzovy.png")
        yellow_image = pygame.image.load("img/mozkomor-zluty.png")
        # typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
        self.mozkomors_images = [blue_image, green_image, purple_image, yellow_image]

        # generujeme mozkomora, kterého chceme chytit
        self.mozkomor_catch_type = random.randint(0, 3)
        self.mozkomor_catch_image = self.mozkomors_images[self.mozkomor_catch_type]
        self.mozkomor_catch_image_rect = self.mozkomor_catch_image.get_rect()
        self.mozkomor_catch_image_rect.centerx = width//2
        self.mozkomor_catch_image_rect.top = 25

    # Kód, který je volán stále dokola
    def update(self):
        self.slow_down_cycle += 1
        if self.slow_down_cycle == 60:
            self.round_time += 1
            self.slow_down_cycle = 0

        # Kontrolu kolize
        self.check_collisions()

    # Vykresluje vše ve hře - texty, hledaného mozkomora
    def draw(self):
        dark_yellow = pygame.Color("#938f0c")
        blue = (21, 31, 217)
        green = (24, 194, 38)
        purple = (195, 23, 189)
        yellow = (195, 181, 23)
        # typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
        colors = [blue, green, purple, yellow]

        # Nastavení textů
        catch_text = self.potter_font.render("Chyt tohoto mozkomora", True, dark_yellow)
        catch_text_rect = catch_text.get_rect()
        catch_text_rect.centerx = width // 2
        catch_text_rect.top = 5

        score_text = self.potter_font.render(f"Skore: {self.score}", True, dark_yellow)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 4)

        lives_text = self.potter_font.render(f"Zivoty: {self.our_player.lives}", True, dark_yellow)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topleft = (10, 30)

        round_text = self.potter_font.render(f"Kolo: {self.round_number}", True, dark_yellow)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (10, 60)

        time_text = self.potter_font.render(f"Cas kola: {self.round_time}", True, dark_yellow)
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (width - 5, 5)

        # Počet, kolikrát se může Harry vrátit do bezpečné zóny
        back_safe_zone_text = self.potter_font.render(f"Bezpecna zona: {self.our_player.enter_safe_zone}", True, dark_yellow)
        back_safe_zone_text_rect = back_safe_zone_text.get_rect()
        back_safe_zone_text_rect.topright = (width - 5, 35)

        # Vykreslení (blitting) do obrazovky
        screen.blit(catch_text, catch_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(lives_text, lives_text_rect)
        screen.blit(round_text, round_text_rect)
        screen.blit(time_text, time_text_rect)
        screen.blit(back_safe_zone_text, back_safe_zone_text_rect)
        # Obrázek mozkomora, kterého máme chytit
        screen.blit(self.mozkomor_catch_image, self.mozkomor_catch_image_rect)

        # Tvary
        # Rámeček herní plochy pro mozkomory - kde se mohou mozkomorové pohybovat
        pygame.draw.rect(screen, colors[self.mozkomor_catch_type], (0, 100, width, height - 200), 4)

    # Kontroluje kolizi Harryho s mozkomorem
    def check_collisions(self):
        # s jakým mozkomorem jsme se srazili?
        collided_mozkomor = pygame.sprite.spritecollideany(self.our_player, self.group_of_mozkomors)

        if collided_mozkomor:
            # Srazili jsme se se správným mozkomorem?
            if collided_mozkomor.type == self.mozkomor_catch_type:
                # Přehrajeme zvuk chycení správného mozkomora
                self.our_player.catch_sound.play()
                # Zvýšíme skóre
                self.score += 10 * self.round_number
                # Odstranění chyceného mozkomora
                collided_mozkomor.remove(self.group_of_mozkomors)
                # Existují další mozkomorové, které můžeme chytat?
                if self.group_of_mozkomors:
                    self.choose_new_target()
                else:
                    # Kolo je dokončené - všechny mozkomory jsme chytili
                    self.our_player.reset()
                    self.start_new_round()
            else:
                self.our_player.wrong_sound.play()
                self.our_player.lives -= 1
                # Je hra u konce = došly životy?
                if self.our_player.lives <= 0:
                    self.pause_game(f"Dosazene skore: {self.score}", "Stisknete enter, pokud chcete hrat znovu!")
                    self.reset_game()
                self.our_player.reset()

    # Zahájí nové kolo - s větším počtem mozkomorů v herní ploše
    def start_new_round(self):
        # Při dokončení kola poskytneme bonus podle toho, jak rychle hráč kolo dokončí: dříve = více bodů
        self.score += int(100 * (self.round_number / (1 + self.round_time)))

        # Resetujeme hodnoty
        self.round_time = 0
        self.slow_down_cycle = 0
        self.round_number += 1
        self.our_player.enter_safe_zone += 1

        # Vyčistíme skupinu mozkomorů, abychom mohli skupinu naplnit novými mozkomory
        for deleted_mozkomor in self.group_of_mozkomors:
            self.group_of_mozkomors.remove(deleted_mozkomor)

        for i in range(self.round_number):
            self.group_of_mozkomors.add(
                Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), self.mozkomors_images[0], 0)
            )

            self.group_of_mozkomors.add(
               Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), self.mozkomors_images[1], 1)
            )

            self.group_of_mozkomors.add(
                Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), self.mozkomors_images[2], 2)
            )

            self.group_of_mozkomors.add(
                Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), self.mozkomors_images[3], 3)
            )

            # Vybíráme nového mozkomora, kterého máme chytit
            self.choose_new_target()

    # Vybírá nového mozkomora, kterého máme chytit
    def choose_new_target(self):
        new_mozkomor_to_catch = random.choice(self.group_of_mozkomors.sprites())
        self.mozkomor_catch_type = new_mozkomor_to_catch.type
        self.mozkomor_catch_image = new_mozkomor_to_catch.image

    # Pozastavení hry - pauza před zahájením nové hry, na začátku při spuštění
    def pause_game(self, main_text, subheading_text):

        global lets_continue

        # Nastavíme barvy
        dark_yellow = pygame.Color("#938f0c")
        black = (0, 0, 0)

        # Hlavní text pro pauznutí
        main_text_create = self.potter_font_big.render(main_text, True, dark_yellow)
        main_text_create_rect = main_text_create.get_rect()
        main_text_create_rect.center = (width//2, height//2 - 35)

        # Podnadpis pro pauznutí
        subheading_text_create = self.potter_font_big.render(subheading_text, True, dark_yellow)
        subheading_text_create_rect = subheading_text_create.get_rect()
        subheading_text_create_rect.center = (width//2, height//2 + 20)

        # Zobrazení hlavního textu a podnadpisu
        screen.fill(black)
        screen.blit(main_text_create, main_text_create_rect)
        screen.blit(subheading_text_create, subheading_text_create_rect)
        pygame.display.update()

        # Zastavení hry
        paused = True
        while paused:
            for one_event in pygame.event.get():
                if one_event.type == pygame.KEYDOWN:
                    if one_event.key == pygame.K_RETURN:
                        paused = False
                if one_event.type == pygame.QUIT:
                    paused = False
                    lets_continue = False

    # Resetuje hru do výchozího stavu
    def reset_game(self):
        self.score = 0
        self.round_number = 0

        self.our_player.lives = 5
        self.our_player.enter_safe_zone = 3
        self.start_new_round()

        # Spuštění muziky v pozadí
        pygame.mixer.music.play(-1, 0.0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("img/potter-icon.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = width//2
        self.rect.bottom = height

        self.lives = 5
        self.enter_safe_zone = 3
        self.speed = 8

        self.catch_sound = pygame.mixer.Sound("media/expecto-patronum.mp3")
        self.catch_sound.set_volume(0.1)
        self.wrong_sound = pygame.mixer.Sound("media/wrong.wav")
        self.wrong_sound.set_volume(0.1)

    # Kód, který je volán stále dokola
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 100:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < height - 100:
            self.rect.y += self.speed

    # Návrat do bezpečné zóny dole v herní ploše
    def back_to_safe_zone(self):
        if self.enter_safe_zone > 0:
            self.enter_safe_zone -= 1
            self.rect.bottom = height

    # Vrací hráče zpět na výchozí pozici - doprostřed bezpečné zóny
    def reset(self):
        self.rect.centerx = width//2
        self.rect.bottom = height


class Mozkomor(pygame.sprite.Sprite):
    def __init__(self, x, y, image, mozkomor_type):
        super().__init__()
        # nahrajeme obrázek mozkomora a umístíme ho
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
        self.type = mozkomor_type

        # nastavení náhodného směru mozkomora
        self.x = random.choice([-1, 1])
        self.y = random.choice([-1, 1])
        self.speed = random.randint(1, 5)

    # Kód, který je volán stále dokola
    def update(self):
        # pohyb mozkomora
        self.rect.x += self.x * self.speed
        self.rect.y += self.y * self.speed

        # odraz mozkomora
        if self.rect.left < 0 or self.rect.right > width:
            self.x = -1 * self.x
        if self.rect.top < 100 or self.rect.bottom > height - 100:
            self.y = -1 * self.y


# Skupina mozkomorů
mozkomor_group = pygame.sprite.Group()
# Testovací mozkomorové
# typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-modry.png"), 0)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zeleny.png"), 1)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-ruzovy.png"), 2)
# mozkomor_group.add(one_mozkomor)
# one_mozkomor = Mozkomor(500, 500, pygame.image.load("img/mozkomor-zluty.png"), 3)
# mozkomor_group.add(one_mozkomor)

# Skupina hráčů
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# Objekt Game
my_game = Game(one_player, mozkomor_group)
my_game.pause_game("Harry Potter a bitva s mozkomory", "Stiskni enter pro zahajeni hry")
my_game.start_new_round()

# Hlavní cyklus hry
lets_continue = True
while lets_continue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lets_continue = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                one_player.back_to_safe_zone()

    # Vyplnění plochy
    # screen.fill((0, 0, 0))
    screen.blit(my_game.background_image, my_game.background_image_rect)

    # Updatujeme skupinu mozkomorů
    mozkomor_group.draw(screen)
    mozkomor_group.update()
    # Updatujeme skupinu hráčů (jeden hráč)
    player_group.draw(screen)
    player_group.update()
    # Updatujeme objekt vytvořený podle classy Game
    my_game.update()
    my_game.draw()

    # Updat obrazovky
    pygame.display.update()

    # Zpomelní cyklu
    clock.tick(fps)

# Ukončení hry
pygame.quit()

