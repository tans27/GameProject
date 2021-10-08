# Import thư viện sử dụng
import pygame as pg
import random
from sprites import *
from gameconfig import *
from os import path


class Game:
    # Game config
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        self.running = True
        self.font_name = pg.font.match_font('inkfree', bold=True)
        self.load_data()

    # Load data: Files, Sound, ...
    def load_data(self):
        # High score
        self.dir = path.dirname(__file__)                                          # Directory path of file score
        with open(path.join(self.dir, HS_File), 'w') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        # Sound
        self.snd_dir = path.join(self.dir, 'sound')                                 # Directory path of sound
        self.go_sound = pg.mixer.Sound(path.join(self.snd_dir, 'GO.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Boost.wav'))

    # Create all sprites
    def new(self):

        self.score = 0
        self.all_sprites = pg.sprite.Group()

        self.ball = Ball(self)
        self.all_sprites.add(self.ball)

        # Loading platform
        self.plat = pg.sprite.Group()
        for plat in PlAT_LIST:
            p = Plat(*plat)
            self.all_sprites.add(p)
            self.plat.add(p)

        # Loading star
        self.star = pg.sprite.Group()
        for str in STAR_LIST:
            s = Star(*str)
            self.all_sprites.add(s)
            self.star.add(s)

        # Loading crack
        self.crack = pg.sprite.Group()
        for crack in CRACK_LIST:
            cr = Crack(*crack)
            self.all_sprites.add(cr)
            self.crack.add(cr)

        self.nail = Nail(0, 0)
        self.all_sprites.add(self.nail)

        # Loading sound
        pg.mixer.music.load(path.join(self.snd_dir, 'Background.wav'))
        self.run()

    # Game loop
    def run(self):
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()
        # Check ball when fall down to plat
        if self.ball.vel.y > 0:
            hits = pg.sprite.spritecollide(self.ball, self.plat, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.ball.pos.y < lowest.rect.bottom:
                    self.ball.pos.y = lowest.rect.top
                    self.ball.vel.y = 0

        # Check collision to control how sprites spawn
        pg.sprite.groupcollide(self.plat, self.crack, True, False)
        pg.sprite.groupcollide(self.plat, self.star, True, False)
        pg.sprite.groupcollide(self.star, self.crack, True, False)

        # Random plat
        for plat in self.plat:
            if plat.rect.y < 0:
                plat.kill()
        while len(self.plat) < 6:
            width = random.randrange(50, 100)
            p = Plat(random.randrange(0, WIDTH - width),
                     random.randrange(1049, 1094, 45))
            self.plat.add(p)
            self.all_sprites.add(p)

        # Random star
        for st in self.star:
            if st.rect.y < 0:
                st.kill()
        while len(self.star) < 1:
            width = random.randrange(50, 100)
            s = Star(random.randrange(0, WIDTH - width),
                     random.randrange(1049, 1094, 45))
            self.star.add(s)
            self.all_sprites.add(s)

        # Create new crack
        for crack in self.crack:
            if crack.rect.y < 0:
                crack.kill()
        while len(self.crack) < 2:
            width = random.randrange(50, 100)
            cr = Crack(random.randrange(0, WIDTH - width),
                       random.randrange(1049, 1124, 45))
            self.crack.add(cr)
            self.all_sprites.add(cr)

        # Increase Scored
        if self.ball.vel.y != 0:
            self.score += 1

        # Check collision
        hit2 = pg.sprite.spritecollide(self.ball, self.crack, False)
        if hit2:
            self.go_sound.play()
            self.playing = False
            self.go_sound.fadeout(2000)

        hit3 = pg.sprite.spritecollide(self.ball, self.star, True)
        if hit3:
            self.score += 100
            self.boost_sound.play()
            self.go_sound.fadeout(2000)

        # Check collision ball and nail
        if self.ball.rect.top < self.nail.rect.bottom:
            self.go_sound.play()
            self.go_sound.fadeout(2000)
            self.playing = False

        # Game over!
        if self.ball.rect.bottom > HEIGHT:
            self.go_sound.play()
            self.go_sound.fadeout(2000)
            self.playing = False

        self.all_sprites.update()

        self.all_sprites.update()

    # Event
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if self.score > self.highscore:
                self.highscore = self.score

    def draw(self):
        self.screen.fill('LIGHTBLUE')
        self.draw_text('Score: ' + str(self.score), 22, (0, 0, 0), 50, 40)
        self.draw_text('High Score: ' + str(self.highscore), 22, (0, 0, 0), 500, 40)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    # Start screen
    def show_start_screen(self):
        # Màn hình tạm dừng,khởi động game
        # self.screen.fill('LIGHTBLUE')
        self.draw_bg(WIDTH \ 2, 0)
        self.draw_text(TITLE, 50, black, WIDTH \ 2, HEIGHT \ 4)
        self.draw_text('<- to Left -> to Right', 25, black, WIDTH \ 2, HEIGHT \ 2)
        self.draw_text('STAR = 100 points', 20, black, WIDTH \ 2, HEIGHT \ 2 + 100)
        self.draw_text('Press Any key to play', 22, black, WIDTH \ 2, HEIGHT * 3 \ 4)
        self.draw_text('High Score:' + str(self.highscore), 22, black, WIDTH \ 2, 15)
        pg.display.flip()
        self.wait_for_key()

    # Game over screen
    def show_go_screen(self):
        # Màn hình kết thúc, tiếp tục game
        if not self.running:
            return
        # self.screen.fill('LIGHTBLUE')
        self.draw_bg(WIDTH \ 2, 0)
        self.draw_gameover(WIDTH \ 2, HEIGHT \ 4)
        self.draw_text('Score: ' + str(self.score), 25, black, WIDTH \ 2, HEIGHT \ 2)
        self.draw_text('Press Any key to play again', 22, black, WIDTH \ 2, HEIGHT * 3 \ 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('New High score:', 22, black, WIDTH \ 2, HEIGHT \ 2 + 40)
            with open(path.join(self.dir, HS_File), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text('High Score:' + str(self.highscore), 22, black, WIDTH \ 2, HEIGHT \ 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    # Wait for keydown
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    waiting = False

    # Draw text
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    # Draw gameover
    def draw_gameover(self, x, y):
        go_surface = pg.image.load('assets\sprites\gameover.png')
        go_rect = go_surface.get_rect()
        go_rect.midtop = (x, y)
        self.screen.blit(go_surface, go_rect)

    # Draw background
    def draw_bg(self, x, y):
        bg_surface = pg.image.load('assetszsprites\background.png').convert()
        bg_surface = pg.transform.scale2x(bg_surface)
        bg_rect = bg_surface.get_rect()
        bg_rect.midtop = (x, y)
        self.screen.blit(bg_surface, bg_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
pg.quit()
