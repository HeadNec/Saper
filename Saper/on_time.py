import arcade
from config import (cell_size, SCREEN_WIDTH, SCREEN_HEIGHT, density, number_colors, time_to_lose,
                    gravity_drag, SPARK_TEX, smoke_mutator, SMOKE_TEX, on_time_timer)
import random
from arcade.particles import FadeParticle, Emitter, EmitBurst


class Hero(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.home = arcade.Sprite("images/home.png")
        self.home.scale = 150 / self.home.height

        self.scale = 75 / self.height
        self.speed = (SCREEN_WIDTH - self.width - self.home.width) / on_time_timer
        self.idle_texture = arcade.load_texture("images/item0.png")
        self.texture = self.idle_texture

        self.center_x = self.width // 2
        self.center_y = SCREEN_HEIGHT

        self.jump = False

        self.walking_textures = []
        for i in range(0, 11):
            texture = arcade.load_texture(f"images/item{i}.png")
            self.walking_textures.append(texture)

        self.texture_change_time = 0
        self.current_texture = 0
        self.texture_change_delay = 0.3
        self.is_walking = True

    def update_animation(self, delta_time: float = 1 / 60):
        if self.is_walking:
            self.texture_change_time += delta_time

            if self.texture_change_time > self.texture_change_delay:
                self.texture_change_time = 0
                self.current_texture += 1

                if self.current_texture >= len(self.walking_textures):
                    self.current_texture = 0

            self.texture = self.walking_textures[self.current_texture]

        else:
            self.texture = self.idle_texture

    def update(self, delta_time: float = 1 / 60):
        self.change_x = self.speed * delta_time
        if self.jump:
            self.change_y = 0
            self.center_y += 5
            if self.center_y >= (SCREEN_HEIGHT - self.height // 2):
                self.jump = False
        else:
            self.change_y = -5
        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
        self.center_y = max(self.height / 2, min(SCREEN_HEIGHT - self.height / 2, self.center_y))

    def Jump(self):
        self.jump = True


class On_time(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.rows = (SCREEN_HEIGHT - 150) // cell_size
        self.cols = SCREEN_WIDTH // cell_size

        self.time = 0

        self.boom = arcade.load_sound("sounds/BOOM.wav")

        self.mine_sprites = arcade.SpriteList()
        self.flag_sprites = arcade.SpriteList()
        self.ping_list = arcade.SpriteList()
        self.lines = arcade.SpriteList()
        self.emitters = []

        self.game_over = False
        self.game_win = False

        self.mines_count = 0
        self.cells_open = 0
        self.cells = self.rows * self.cols

        self.grid = self.create_grid()

        self.open = []
        self.create_sprites()

        self.text = arcade.Text(f"Всего бомб - {self.mines_count}", cell_size // 2, SCREEN_HEIGHT - (cell_size // 2 + 10),
                                arcade.color.WHITE, cell_size // 2)

    def create_sprites(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_size + cell_size // 2
                y = row * cell_size + cell_size // 2

                if self.grid[row][col][0] == "b":
                    mine = arcade.Sprite("images/bomb.png")
                    mine.scale = cell_size / mine.width
                    mine.center_y = y
                    mine.center_x = x
                    mine.visible = False
                    self.mine_sprites.append(mine)

                flag = arcade.Sprite("images/flag.png")
                flag.center_x = x
                flag.center_y = y
                flag.visible = False
                flag.scale = (cell_size - 5) / flag.width
                self.flag_sprites.append(flag)

        self.hero = Hero()
        self.ping_list.append(self.hero)

        self.home = arcade.Sprite("images/home.png")
        self.home.scale = 150 / self.home.height
        self.home.center_y = SCREEN_HEIGHT - 150 + self.home.height // 2
        self.home.center_x = SCREEN_WIDTH - self.home.width // 2
        self.ping_list.append(self.home)

        dx = 0
        for i in range(0, 12):
            line = arcade.Sprite("images/line.png")
            line.scale = 0.05
            line.center_y = SCREEN_HEIGHT - 150
            line.center_x = dx
            dx += line.width
            self.lines.append(line)

        self.physics_engine = arcade.PhysicsEngineSimple(self.hero, self.lines)


    def create_grid(self):
        grid = [[[0, 0] for _ in range(self.cols)] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.cols):
                grid[i][j] = ["b", 0] if random.random() < density else [0, 0]
                if grid[i][j][0] == "b":
                    self.mines_count += 1

        for r in range(self.rows // 2 - 1, self.rows // 2 + 2):
            for c in range(self.cols // 2 - 3, self.cols // 2):
                if grid[r][c][0] == "b":
                    self.mines_count -= 1
                grid[r][c][1] = 1
                grid[r][c][0] = 0
                self.cells_open += 1


        for i in range(self.rows):
            for j in range(self.cols):
                if grid[i][j][0] != "b":
                    bombs = 0
                    for row in range(max(0, i - 1), min(self.rows, i + 2)):
                        for col in range(max(0, j - 1), min(self.cols, j + 2)):
                            if grid[row][col][0] == "b":
                                bombs += 1
                            if row == i and col == j:
                                continue
                    grid[i][j] = [bombs, grid[i][j][1]]
        return grid

    def mine_boom(self, x, y, count=80):
        self.boom.play()

        self.emitters.append(Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda e: FadeParticle(
                filename_or_texture=random.choice(SPARK_TEX),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.1),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.35, 0.6),
                mutation_callback=gravity_drag,
            ),
        ))

        self.emitters.append(Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(12),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=SMOKE_TEX,
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
            lifetime=random.uniform(1.5, 2.5),
            start_alpha=200, end_alpha=0,
            scale=random.uniform(0.6, 0.9),
            mutation_callback=smoke_mutator,
        ),
    ))

    def on_draw(self):
        self.clear()

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_size + cell_size // 2
                y = row * cell_size + cell_size // 2

                if self.grid[row][col][1] == 0:
                    arcade.draw_rect_filled(arcade.rect.XYWH(x, y,
                                                             cell_size - 2,
                                                             cell_size - 2),
                                            arcade.color.WHITE)

                else:
                    arcade.draw_rect_filled(arcade.rect.XYWH(x, y,
                                                             cell_size - 2,
                                                             cell_size - 2),
                                            arcade.color.DARK_GRAY)
                    if self.grid[row][col][0] != "b":
                        color = number_colors[self.grid[row][col][0]]
                        arcade.draw_text(str(self.grid[row][col][0]), x - 10, y - 10, color, cell_size // 2)

                arcade.draw_rect_outline(arcade.rect.XYWH(x, y,
                                                          cell_size - 2,
                                                          cell_size - 2),
                                         arcade.color.BLACK, 1)

        self.mine_sprites.draw()
        self.flag_sprites.draw()
        self.text.draw()
        self.ping_list.draw()
        self.lines.draw()

        for e in self.emitters:
            e.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()
        if self.game_over:
            from gui import LoseGame
            self.time += delta_time
            if self.time >= time_to_lose:
                self.window.show_view(LoseGame())

        if (self.cells - self.cells_open) == self.mines_count:
            from gui import WinGame
            self.window.show_view(WinGame())

        for emitter in self.emitters:
            emitter.update()
            if emitter.can_reap():
                self.emitters.remove(emitter)

        self.hero.update_animation()
        self.hero.update()
        if arcade.check_for_collision(self.hero, self.home):
            from gui import LoseGame
            self.window.show_view(LoseGame())

    def on_mouse_press(self, x, y, button, modifiers):
        col = int(x // cell_size)
        row = int(y // cell_size)

        x = col * cell_size + cell_size // 2
        y = row * cell_size + cell_size // 2

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.grid[row][col][0] == "b":
                mines = arcade.get_sprites_at_point((x, y), self.mine_sprites)
                for mine in mines:
                    mine.visible = True
                    self.mine_boom(mine.center_x, mine.center_y)
                self.game_over = True

            if self.grid[row][col][1] == 0 and self.grid[row][col][0] != "b":
                self.grid[row][col][1] = 1
                self.cells_open += 1

        if button == arcade.MOUSE_BUTTON_RIGHT:
            flags = arcade.get_sprites_at_point((x, y), self.flag_sprites)
            for flag in flags:
                if flag.visible:
                    flag.visible = False
                elif not flag.visible and self.grid[row][col][1] == 0:
                    flag.visible = True

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.hero.Jump()