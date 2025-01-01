import pygame as pg
from pygame.math import Vector2 as V2, Vector3 as V3
from random import randint, choice, sample
from math import sin
pg.init()
font60 = pg.font.Font(None, 60)
font30 = pg.font.Font(None, 30)
font60.bold = True
TILE = (20, 20)
SHAPES = {0:[(-1,-2),(-1,-1),(0,-1),(0,0)],
          1:[(0,-2),(0,-1),(-1,-1),(-1,0)],
          2:[(0,-1),(-1,0),(0,0),(1,0)],
          3:[(0,-2),(0,-1),(0,0),(0,1)],
          4:[(0,-2),(0,-1),(-1,0),(0,0)],
          5:[(-1,-2),(-1,-1),(-1,0),(0,0)],
          6:[(-1,-1),(0,-1),(-1,0),(0,0)]}
MOVE_BlOK = pg.USEREVENT + 2
pg.time.set_timer(MOVE_BlOK, 200)
TICK = pg.USEREVENT + 3
pg.time.set_timer(TICK,150)


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((800,600))
        self.clock = pg.time.Clock()
        self.running = True
        self.pause = False
        self.new_game = True
        self.resume = None
        self.options = None
        self.quit_game = None
        self.menu_status = 'main'
        self.difficulty = 1
        self.theme = 0
        self.tiles = pg.sprite.Group()
        self.control = {'move left': pg.K_LEFT, 'move right': pg.K_RIGHT,
                        'turn left': pg.K_UP, 'turn right': pg.K_DOWN,
                        'jump': pg.K_SPACE, 'pick': pg.K_LCTRL}
        self.set_key_rect = None
        self.set_key_name = None
        self.blocks = pg.sprite.Group()
        self.falling_tiles = pg.sprite.Group()
        self.menu_tiles = pg.sprite.Group()
        self.debris = pg.sprite.Group()
        self.timer = 0
        self.clouds = []
        self.ground = pg.Rect((0,540,800,600))
        self.level = Level()
        self.cur_level = 0
        self.player = Player()
        self.dt = 0
        self.tiles_mask = None
    def run(self):
        while self.running:
            self.screen.fill((120, 130, 120))
            self.sky()
            if self.pause or self.new_game: self.menu(); self.menu_tiles.draw(self.screen)
            else:
                self.level.draw(self.cur_level, self.screen)
                self.create_block()
                self.tiles.draw(self.screen)
                self.make_tiles_mask()
                self.player.update()
                self.player.draw(self.screen)
                self.level.check_overlap(self.cur_level)
                if self.debris:
                    self.debris.update()
                    self.debris.draw(self.screen)
            self.event_handler()
            pg.display.flip()
            self.clock.tick(60)
    def event_handler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.menu_status == 'options': self.menu_status = 'main'; self.menu_tiles.empty()
                    elif self.menu_status == 'main': self.pause = not self.pause
                if self.set_key_rect and self.set_key_name:
                    self.control[self.set_key_name] = event.key
                    self.set_key_name = self.set_key_rect = None
            if event.type == MOVE_BlOK:
                if not (self.pause or self.new_game): self.blocks.update();self.new_cloud()
            if event.type == TICK: self.dt += 1
    def create_block(self):
        if not self.timer % {2: 150, 1: 300, 0: 500}.get(self.difficulty):
            pos = V2(randint(2,38),-2)
            block = Block(randint(0,6), pos * 20, [(220,)*3,(70,)*3][self.theme], [self.tiles, self.falling_tiles], self.blocks)
            block.rotate(choice([-90,0,90]))
        self.timer += 1
    def menu(self):
        self.resume = Button((250, 100), ['RESUME', 'PLAY'][self.new_game])
        self.options = Button((250, 250), 'OPTIONS')
        self.quit_game = Button((250, 400), 'QUIT')
        if self.menu_status == 'main':
            if self.resume.draw(self.screen): self.pause = False; self.new_game = False
            if self.options.draw(self.screen): self.menu_status = 'options'
            if self.quit_game.draw(self.screen): self.running = False
        elif self.menu_status == 'options':
            self.settings()
    def settings(self):
        self.screen.blit(font60.render('DIFFICULTY', True, (50, 50, 50)),(100,100))
        self.screen.blit(font60.render('THEME', True, (50, 50, 50)), (100, 250))
        self.screen.blit(font60.render('CONTROL', True, (50, 50, 50)), (100, 400))
        e = pg.draw.rect(self.screen, (200,200,200), (400, 100, 100, 30),0,10)
        n = pg.draw.rect(self.screen, (150,150,150), (510, 90, 100, 40), 0, 10)
        h = pg.draw.rect(self.screen, (80,80,80), (620, 80, 100, 50), 0, 10)
        self.screen.blit(font30.render('easy', True, (50, 50, 50)), (427, 105))
        self.screen.blit(font30.render('normal', True, (50, 50, 50)), (525, 105))
        self.screen.blit(font30.render('hard', True, (50, 50, 50)), (647, 105))
        selection = [e, n, h][self.difficulty]
        pg.draw.rect(self.screen, (180, 50, 50), selection, 3, 10)
        rest = self.screen.blit(font60.render('RESTART', True, (150,)*3),(100,553))
        back = self.screen.blit(font60.render('BACK', True, (150,)*3),(400,553))
        play = self.screen.blit(font60.render('PLAY', True, (150,)*3),(610,553))
        if rest.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            self.__init__()
            self.run()
        if back.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            self.menu_status = 'main'
            self.menu_tiles.empty()
        if play.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            self.pause = False
            self.new_game = False
        l = pg.Rect(405,150,150,150)
        d = pg.Rect(565,150,150,150)
        pg.draw.rect(self.screen, (180, 50, 50), [l,d][self.theme], 3, 10)
        self.theme_menu()
        if self.new_game:
            for theme, i in enumerate([l, d]):
                if i.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                    self.theme = theme
                    self.menu_tiles.empty()
            for diff, i in enumerate([e, n, h]):
                if i.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]: self.difficulty = diff
        self.screen.blit(font30.render('move left', True, (50, 50, 50)), (400, 400))
        self.screen.blit(font30.render('move right', True, (50, 50, 50)), (400, 485))
        self.screen.blit(font30.render('turn left', True, (50, 50, 50)), (520, 400))
        self.screen.blit(font30.render('turn right', True, (50, 50, 50)), (520, 485))
        self.screen.blit(font30.render('jump', True, (50, 50, 50)), (640, 400))
        self.screen.blit(font30.render('pick&drop', True, (50, 50, 50)), (640, 485))
        m_l = pg.draw.rect(self.screen, (150, 150, 150), (400, 345, 100, 50), 0, 10)
        m_r = pg.draw.rect(self.screen, (150, 150, 150), (400, 430, 100, 50), 0, 10)
        t_l = pg.draw.rect(self.screen, (150, 150, 150), (520, 345, 100, 50), 0, 10)
        t_r = pg.draw.rect(self.screen, (150, 150, 150), (520, 430, 100, 50), 0, 10)
        j = pg.draw.rect(self.screen, (150, 150, 150), (640, 345, 100, 50), 0, 10)
        p = pg.draw.rect(self.screen, (150, 150, 150), (640, 430, 100, 50), 0, 10)
        for key, name in zip([m_l,m_r,t_l,t_r,j,p],['move left','move right','turn left','turn right','jump','pick']):
            key_name = pg.key.name(self.control[name])
            key_label = font30.render(key_name, True, (180, 50, 50))
            label_rect = key_label.get_rect(center=key.center)
            self.screen.blit(key_label, label_rect)
            if key.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] and self.new_game: # TODO добавить проверку на уже занятые клавиши управления
                self.set_key_rect = key
                self.set_key_name = name
            if self.set_key_rect: pg.draw.rect(self.screen, (180, 50, 50), self.set_key_rect, 3, 10)
    def new_cloud(self):
        rad = randint(30, 100)
        speed = randint(1, 3)
        pos = V2(randint(850, 900), -randint(rad//3, rad))
        color = randint(100, 120)
        self.clouds.append([pos, rad, speed, color])
    def sky(self):
        for i in self.clouds:
            p, r, s, c = i
            pg.draw.circle(self.screen, (c,c,c+20), p, r)
            if (new_pos := p - V2(s,0)).x < -r: self.clouds.remove(i)
            else: i[0] = new_pos
        self.ground = pg.draw.rect(self.screen,(50,80,50),self.ground)
    def theme_menu(self):
        layout = ['000111','111111','222212','113122','133321']
        themes = [0, (255, 130, 120), (220,)*3, (240, 180, 180)],[0, (255, 130, 120), (70,) * 3, (90, 30, 30)]
        poss = V2(420,185), V2(580,185)
        for pos, theme in zip(poss,themes):
            for y,colors in enumerate(layout):
                for x,c in enumerate(colors):
                    if c !='0': pg.draw.rect(self.screen, theme[int(c)], (pos.x+x*20, pos.y+y*20, 18, 18), c=='1', 3)
    def make_tiles_mask(self):
        surf = pg.Surface(self.screen.get_size())
        surf.set_colorkey('black')
        tile_image = pg.Surface(TILE)
        tile_image.fill('red')
        ground_image = pg.Surface(self.ground.size)
        ground_image.fill('red')
        for tile in self.tiles: surf.blit(tile_image,tile.rect)
        surf.blit(ground_image,self.ground)
        self.tiles_mask = pg.mask.from_surface(surf)

class Button:
    def __init__(self, pos, text):
        self.rect = pg.Rect(*pos,300,100)
        self.text = font60.render(text, True, (50, 50, 50))
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.color = (150,150,150)
    def draw(self, surf):
        mouse_pos = pg.mouse.get_pos()
        collision = self.rect.collidepoint(mouse_pos)
        color = (200, 100, 100) if collision else self.color
        pg.draw.rect(surf, color, self.rect, 0, 10)
        pg.draw.rect(surf, (50, 50, 50), self.rect, 5, 10)
        surf.blit(self.text, self.text_rect)
        return True if collision and pg.mouse.get_pressed()[0] else False

class Block(pg.sprite.Sprite):
    def __init__(self, shape, pos, color, group, blocks):
        super().__init__(blocks)
        self.pos = V2(pos)
        self.shape = shape
        self.shapes = SHAPES[self.shape]
        self.color = color
        self.active = False
        self.picked = False
        self.block_tiles = pg.sprite.Group()
        self.static = False
        self.falling = True
        self.cover = set()
        self.basement = set()
        self.change_color = False
        for offset in self.shapes:
            Tile(self.pos + V2(offset)*TILE[0], self.color, (group, self.block_tiles), self)
        self.rect = self.get_rect()
        self.set_tiles_offset()
    def rotate(self, angl):
        for t in self.block_tiles.sprites():
            rect = t.rect.copy()
            rect.topleft = (rect.topleft - self.pos).rotate(angl)
            if angl > 0: t.rect.topright = rect.topleft + self.pos
            else: t.rect.bottomleft = rect.topleft + self.pos
        self.rect = self.get_rect()
        self.set_tiles_offset()
    def update(self):
        move = V2()
        if self.picked:
            for block in self.basement: block.cover.remove(self)
            self.basement.clear()
        else:
            self.check_static()
            if not (any(t.rect.bottom == game.ground.top for t in self.block_tiles.sprites()) or
                    any(pg.sprite.spritecollide(t, game.tiles, False, self.collide_if_not_self)
                        for t in self.block_tiles.sprites())):
                self.pos.y += TILE[0]
                move.y = TILE[0]
            else:
                if self.falling:
                    collisions = pg.sprite.groupcollide(self.block_tiles, game.tiles, False, False, self.collide_if_not_self)
                    self.falling = False
                    game.falling_tiles.remove(self.block_tiles.sprites())
                    for block_tile, game_tiles in collisions.items():
                        for game_tile in game_tiles:
                            game_tile.parent.cover.add(block_tile.parent)
                            block_tile.parent.basement.add(game_tile.parent)
                            game_tile.parent.update()
            self.block_tiles.update(move, self.change_color, self.active)
            self.active = False
            self.rect.move_ip(move)
            self.set_tiles_offset()
    def collide_if_not_self(self, left, right):
        if right not in self.block_tiles.sprites():
            return left.rect.move(0,5).colliderect(right)
        return False
    def check_static(self):
        if (self.cover and not self.static) or (not self.cover and self.static):
            self.static = not self.static
            self.change_color = True
        else: self.change_color = False
    def get_rect(self):
        rects = [tile.rect for tile in self.block_tiles]
        return rects[0].unionall(rects[1:])
    def set_tiles_offset(self):
        for tile in self.block_tiles:
            tile.offset = V2(tile.rect.topleft) - V2(self.rect.topleft)

class Tile(pg.sprite.Sprite):
    def __init__(self, pos, color, groups, parent):
        super().__init__(*groups)
        self.color = [color, V3(color)-V3(-20,40,40)]
        self.style = 0
        self.parent = parent
        self.pos = pos
        self.image = pg.Surface(TILE)
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect(topleft=self.pos)
        self.put_color(self.color[self.style])
        self.offset = None
    def update(self, move, change_color, active=False):
        self.rect.move_ip(move)
        if change_color: self.style = self.style ^ change_color
        self.put_color(self.color[self.style])
        if active: pg.draw.rect(self.image, 'green', (1, 1, 18, 18), 2, 3)
    def put_color(self, color):
        pg.draw.rect(self.image, color, (1, 1, 18, 18), 0, 3)

class Debris(pg.sprite.Sprite):
    def __init__(self,image,rect,group):
        super().__init__(group)
        self.image = self.surf = image
        self.rect = rect
        self.speed_x = randint(-2,2)
        self.speed_y = randint(-6,-3)
        self.rotation_speed = randint(-10,10)
        self.angl = 0
        self.timer = 20
        self.gravity = 1
        self.alpha = 255
    def update(self):
        self.rect.move_ip(self.speed_x, self.speed_y)
        self.image = pg.transform.rotate(self.surf,self.angl)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.angl += self.rotation_speed
        self.timer -= 1.2
        self.speed_y += self.gravity
        self.alpha -= 5
        self.image.set_alpha(self.alpha)
        if self.timer <= 0: self.kill()

class Level:
    def __init__(self):
        self.task_map = [[(26,'0000000000000001111111111000000000000000'),
                          (25,'0000000000000001111111111000000000000000')],
                         [(26,'1111111111000000000000000000001111111111'),
                          (25,'0111111111100000000000000000011111111110'),
                          (24,'0011111111110000000000000000111111111100')],
                         [(26,'1111111111111111111111111111111111111111'),
                          (25,'1111111111111111111111111111111111111111'),
                          (24,'0000011111111111111111111111111111100000')],
                         [(20,'0000000000000000000011111111110000000000'),
                          (21,'0000000000000000000011111111110000000000'),
                          (22,'0000000000000000000011111111110000000000'),
                          (23,'0000000000000000000011111111110000000000'),
                          (24,'0000000000000000000011111111110000000000'),
                          (25,'0000000000000000000011111111110000000000'),
                          (26,'0000000000000000000011111111110000000000')]]
    def draw(self, level, surf):
        for i,r in self.task_map[level]:
            for j,c in enumerate(r):
                if c=='1': pg.draw.rect(surf,(255, 130, 120),(j*20+1,i*20+1,18,18),1,3)
    def check_overlap(self, level):
        level_rects = []
        for i,r in self.task_map[level]:
            for j,c in enumerate(r):
                if c=='1': level_rects.append(pg.Rect(j*20+1,i*20+1,18,18))
        collisions = [1 for rect in level_rects if rect.collideobjects(game.tiles.sprites(), key=lambda o: o.rect)]
        level_blocks_num, finished = len(level_rects), sum(filter(None, collisions))
        game.screen.blit(font30.render(f'Finished: {finished}/{level_blocks_num}', True, 'white'), (150, 570))
        game.screen.blit(font30.render(f'Level: {game.cur_level+1}', True, 'white'), (450, 570))
        if level_blocks_num == finished: self.level_up()
    def level_up(self):
        # todo next level animation
        game.cur_level = (game.cur_level + 1) % len(self.task_map)
        game.tiles.empty()

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = self.get_image()
        self.rect = self.image.get_rect(midbottom=(400,400))
        self.basement_rect = pg.Rect(self.rect.bottomleft,(35,5))
        self.mask = pg.mask.from_surface(pg.Surface((40,60)))
        self.magnet_rect = pg.Rect(self.rect.x + 37, self.rect.y + 30, 3, 20)
        self.magnet_hit_box = pg.Rect(self.rect.right, self.rect.y, 20, self.rect.h)
        self.magnet_active = False
        self.active_magnet_pos = None
        self.direction = V2(1,0)
        self.smoke = []
        self.speed = V2(3,0)
        self.move = 1
        self.jump_start_speed = -14
        self.gravity = 1
        self.jumping = False
        self.can_jump = True
        self.lives = 5
        self.freeze = False
        self.freeze_time = 10
        self.loaded = False
        self.load = None
        self.load_timer = 20
    def get_image(self):
        body = (50,50,50)
        image = pg.Surface((40, 60))
        image.set_colorkey('black')
        pg.draw.rect(image, body, (0, 0, 35, 50), 0, -1, 15, 15, 3, 3)
        pg.draw.line(image, 'black', (0, 14), (35, 14), 3)
        return image
    def update(self):
        keys = pg.key.get_pressed()
        if keys[game.control['move left']] and self.rect.left > 0: self.direction.x = -1; self.move = -1
        elif keys[game.control['move right']] and self.rect.right < 800: self.direction.x = 1; self.move = 1
        else: self.direction.x = 0
        if keys[game.control['jump']] and self.can_jump:
            self.direction.y = -1
            self.jumping = True
            self.can_jump = False
            self.speed.y = self.jump_start_speed
        if keys[game.control['pick']]:
            if self.loaded and not self.jumping: self.drop_block()
            elif not self.loaded and self.magnet_active: self.load_block()
        if self.loaded and keys[game.control['turn left']] and not self.jumping: self.rotate_block(90)
        elif self.loaded and keys[game.control['turn right']] and not self.jumping: self.rotate_block(-90)
        self.rect.move_ip(self.direction.x * self.speed.x, self.speed.y)
        if self.loaded:
            self.load.rect.midbottom = self.rect.midtop
            self.load.rect.y -= 20
            for tile in self.load.block_tiles: tile.rect.topleft = self.load.rect.topleft + tile.offset
        if self.direction.y:
            self.speed.y += self.gravity
            self.speed.y = min(self.speed.y, 14)
            if self.speed.y > 0: self.direction.y = 1
        self.basement_rect.midtop = self.rect.midbottom
        if not self.freeze:
            self.horizontal_collisions()
            self.vertical_collisions()
        self.check_load_collision()
        self.check_freez()
        game.screen.blit(font30.render(f'lives: {self.lives}',True,'white'),(50,570))
        self.magnet_update()
        self.load_timer += 1
    def magnet_update(self):
        self.magnet_rect.x, self.magnet_rect.y = self.rect.x + 37, self.rect.y + 30
        self.magnet_hit_box.x = self.rect.right if self.move == 1 else self.rect.x - 20
        self.magnet_hit_box.y = self.rect.y
        if self.magnet_active: self.magnet_rect.y = self.active_magnet_pos
    def draw(self,surf):
        image = self.image if self.move == 1 else pg.transform.flip(self.image,True,False)
        rect = self.rect.move(0, sin(game.dt)*3)
        if not self.loaded:
            magnet_rect = self.magnet_rect.move(0, sin(game.dt) * 3) if self.move == 1 else self.magnet_rect.move(-37, sin(game.dt) * 3)
        else:
            magnet_rect = pg.Rect(self.rect.x + 10, self.rect.y - 10, 20, 3)
        field_point = magnet_rect.right if self.move == 1 else magnet_rect.left
        field_color = ['cyan', 'red'][self.magnet_active]
        for i in sample(range(20), 12):
            if not self.loaded:
                pg.draw.circle(surf, field_color, (field_point + randint(0, 5) * self.move, self.magnet_rect.top + i), 1)
            else:
                pg.draw.circle(surf, 'red', (magnet_rect.left + i, magnet_rect.top - randint(0, 8)), 1)
        for i in range(5):
            pg.draw.circle(self.image, 'red' if game.dt % 5 == i else 'green', (7 + i * 5, 10), 2)
        surf.blit(image, rect)
        pg.draw.rect(surf, (50,50,50), magnet_rect)
        self.smoke.append(
            [(randint(rect.left, rect.right), rect.bottom - randint(0,3)), randint(3, 6), randint(50, 150), randint(-4, 4), 255, 4])
        for circ in self.smoke:
            pos, rad, col, speedx, alf, speedy = circ
            color = (255 ,col +100,0, alf) if self.jumping else (col,col,col, alf)
            pg.draw.circle(surf, color, pos, rad)
            d = V2(speedx, speedy)
            pos = V2(pos) + d
            alf -= 40
            speedy -= 2
            if alf < 0: self.smoke.remove(circ)
            else:
                for i, param in enumerate([pos, rad, col, speedx, alf, speedy]): circ[i] = param
    def vertical_collisions(self):
        self.check_collision()
        if self.overlap_rect:
            w, h = self.overlap_rect.size
            if self.direction.y < 0 and self.rect.top == self.overlap_rect.top:
                self.bouncing_down(); self.speed.x = 0
            elif self.direction.y > 0:
                if self.rect.bottom == self.overlap_rect.bottom: self.landing()
            elif self.direction.y == 0 and self.rect.top == self.overlap_rect.top: self.live_lost()
    def horizontal_collisions(self):
        self.check_collision()
        if self.overlap_rect:
            w, h = self.overlap_rect.size
            if self.direction.x > 0 and self.rect.right == self.overlap_rect.right:
                if self.direction.y > 0 and w > h and self.rect.bottom == self.overlap_rect.bottom: self.landing()
                elif self.direction.y < 0 and w > h and self.rect.top == self.overlap_rect.top: self.bouncing_down()
                elif w <= 6: self.rect.right = self.overlap_rect.left
            elif self.direction.x < 0 and self.rect.left == self.overlap_rect.left:
                if self.direction.y > 0 and w > h and self.rect.bottom == self.overlap_rect.bottom: self.landing()
                elif self.direction.y < 0 and w > h and self.rect.top == self.overlap_rect.top: self.bouncing_down()
                elif w <= 6: self.rect.left = self.overlap_rect.right
    def check_collision(self):
        basement_collision = self.check_basement_collision()
        if not basement_collision and not self.jumping: self.direction.y = 1
        overlap_mask = game.tiles_mask.overlap_mask(self.mask,self.rect.topleft)
        rects_overlap = overlap_mask.get_bounding_rects()
        if len(rects_overlap) > 1:
            self.overlap_rect = rects_overlap[0].unionall(rects_overlap[1:])
        elif len(rects_overlap) == 1: self.overlap_rect = rects_overlap[0]
        else: self.overlap_rect = None
        if self.direction.y == -1 and (falling_block_collision := pg.sprite.spritecollide(self,game.falling_tiles,False)):
            self.destroy_block(falling_block_collision)
        sprite_list = game.tiles.sprites()
        if not self.loaded and (indices := self.magnet_hit_box.collidelistall(sprite_list)):
            for index in indices:
                block = sprite_list[index].parent
                if not block.static:
                    block.active = True
                    self.magnet_active = True
                    self.active_magnet_pos = sprite_list[index].rect.y
                    self.load = block
                    break
        else:
            self.magnet_active = False
            self.active_magnet_pos = None
    def check_basement_collision(self):
        sprites = game.tiles.sprites() + [game.ground]
        basement_collisions = self.basement_rect.collidelistall(sprites)
        if basement_collisions:
            collision_rects = [sprites[i].rect if isinstance(sprites[i],Tile) else sprites[i] for i in basement_collisions]
            if len(collision_rects) == 1: return collision_rects[0]
            else: return collision_rects[0].unionall(collision_rects[1:])
        return
    def check_load_collision(self):
        if self.loaded:
            collisions = pg.sprite.groupcollide(self.load.block_tiles, game.tiles, False, False, self.collide_if_not_self)
            if any(collisions.values()): self.destroy_block(self.load.block_tiles); self.loaded = False; self.load = None
    def collide_if_not_self(self, left, right):
        if right not in self.load.block_tiles.sprites():
            return left.rect.colliderect(right)
        return False
    def check_freez(self):
        if self.freeze:
            self.speed *= 0
            self.freeze_time -= 0.1
            self.image.set_alpha(255*int(self.freeze_time%2))
            if self.freeze_time <= 0:
                self.freeze_time = 10
                self.freeze = False
                self.speed = V2(3,self.jump_start_speed)
                self.direction.y = -1
                self.jumping = True
                self.can_jump = False
    def live_lost(self):
        self.lives -= 1
        self.freeze = True
        self.can_jump = False
        if self.lives == 0: game.running = False
    def landing(self):
        self.rect.bottom = self.overlap_rect.top
        self.direction.y = 0
        self.jumping = False
        self.can_jump = True
        self.speed.y = 0
        self.speed.x = 3
    def bouncing_down(self):
        h = min(14, self.overlap_rect.bottom - self.rect.top)
        self.rect.top = self.rect.top + h
        self.speed.y = 0
        self.direction.y = 1
        self.direction.x = 0
    def destroy_block(self,tiles):
        blocks = {tile.parent for tile in tiles}
        debris_sprites = sum([b.block_tiles.sprites() for b in blocks], [])
        for block in blocks: block.kill()
        for sprite in debris_sprites:
            sprite.kill()
            debr_size = randint(5,12)
            img = pg.transform.scale(sprite.image, (debr_size,debr_size))
            for i in range(5): Debris(img, sprite.rect.move(i,i), game.debris)
    def load_block(self):
        if self.load_timer >= 20:
            load_rect = self.load.rect.copy()
            load_rect.midbottom = self.rect.midtop
            load_rect.y -= 20
            if load_rect.collidelist(game.tiles.sprites()) == -1:
                self.loaded = True
                self.load.picked = True
                self.load_timer = 0
                block_offset = self.load.pos - self.load.rect.topleft
                offset = load_rect.topleft - self.load.pos + block_offset
                for tile in self.load.block_tiles: tile.rect.move_ip(offset)
    def drop_block(self):
        if self.load_timer >= 20:
            initial_load_rect_x = self.load.rect.x
            self.load.rect.x = (self.load.rect.right // 20 + 1) * 20 if self.move == 1 else self.load.rect.left // 20 * 20 - self.load.rect.w
            if self.load.rect.left < 0 or self.load.rect.right > 800: self.load.rect.x = initial_load_rect_x; return
            for tile in self.load.block_tiles: tile.rect.topleft = self.load.rect.topleft + tile.offset
            if any(game.tiles_mask.get_at(tile.rect.center) for tile in self.load.block_tiles):
                self.load.rect.x = initial_load_rect_x
                for tile in self.load.block_tiles: tile.rect.topleft = self.load.rect.topleft + tile.offset
            else:
                self.loaded = False
                self.load.picked = False
                self.load.falling = True
                self.load = None
            self.load_timer = 0
    def rotate_block(self, angle):
        if self.load_timer >= 20:
            self.load.rotate(angle)
            self.load_timer = 0

if __name__ == '__main__':
    game = Game()
    game.run()